import discord
import os
import tempfile
import asyncio
from discord.ext import commands
from app.services.moderation_service import ModerationService
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService
from PIL import Image
import io
from pydub import AudioSegment
import numpy as np
import torch

# Load services
moderation_service = ModerationService()
audio_service = AudioService()
meeting_service = MeetingService()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


# -------------------------------
# AUTOMATIC CONTENT MODERATION
# -------------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_inappropriate = False

    if message.attachments:
        for attachment in message.attachments:
            try:
                content_type = attachment.content_type
                if content_type.startswith("image/"):
                    image_bytes = await attachment.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    result = moderation_service.analyze_image(image)
                    is_inappropriate = result.get("is_inappropriate", False)
                    analysis_type = "Image"
                elif content_type.startswith("audio/"):
                    audio_bytes = await attachment.read()
                    result = moderation_service.analyze_audio(audio_bytes)
                    is_inappropriate = result.get("is_inappropriate", False)
                    analysis_type = "Audio"
                elif content_type.startswith("video/"):
                    video_bytes = await attachment.read()
                    result = moderation_service.analyze_video(video_bytes)
                    is_inappropriate = result.get("is_inappropriate", False)
                    analysis_type = "Video"
                else:
                    analysis_type = "Attachment (Unsupported Type)"
                    print(f"Unsupported attachment type: {content_type}")

                if is_inappropriate:
                    print(
                        f"Inappropriate {analysis_type} detected from {message.author.name} in {message.channel.name}, deleting message."
                    )
                    break

            except Exception as e:
                print(f"Error analyzing {analysis_type} attachment: {e}")
                is_inappropriate = False

    else:
        text_result = moderation_service.analyze_text(message.content)
        is_inappropriate = text_result.get("is_inappropriate", False)
        analysis_type = "Text"

    if is_inappropriate:
        await message.delete()
        warning_message = f"⚠️ Your message in {message.channel.name} was removed due to inappropriate content ({analysis_type} analysis)."
        try:
            await message.author.send(warning_message)
        except discord.errors.Forbidden:
            print(f"Could not send DM warning to {message.author.name}")
        print(
            f"Deleted {analysis_type} message from {message.author.name}: {message.content if analysis_type == 'Text' else '<attachment(s)>'}"
        )

    await bot.process_commands(message)


# -------------------------------
# MOM GENERATION (VOICE RECORDING)
# -------------------------------
@bot.command()
async def join(ctx):
    """Joins voice channel and starts recording"""
    if not ctx.author.voice:
        await ctx.send("❌ You must be in a voice channel!")
        return

    channel = ctx.author.voice.channel

    try:
        vc = await channel.connect()
    except discord.ClientException:
        await ctx.send("❌ Already connected to a voice channel!")
        return

    sink = discord.sinks.WaveSink()

    # Proper async callback definition
    vc.start_recording(
        sink,
        finished_callback,  # Direct coroutine reference
        ctx.channel,  # Pass the channel as an argument
    )

    await ctx.send(f"🎙️ Recording started in **{channel.name}**!")


@bot.command()
async def leave(ctx):
    """Stops recording and generates MoM"""
    vc = ctx.voice_client

    if not vc:
        await ctx.send("❌ Not recording in any channel!")
        return

    vc.stop_recording()
    await vc.disconnect()
    await ctx.send("⏳ Stopped recording. Processing meeting minutes...")


async def finished_callback(sink, channel):
    try:
        # 1. Check if we have any audio data
        if not sink.audio_data:
            await channel.send("❌ No audio recorded")
            return

        # 2. Combine audio data from all users
        audio_data_parts = []
        for user, data in sink.audio_data.items():
            audio_bytes = data.file.read()
            if audio_bytes:  # Only add non-empty audio data
                audio_data_parts.append(audio_bytes)

        if not audio_data_parts:
            await channel.send("❌ Recorded audio is empty")
            return

        audio_data = b"".join(audio_data_parts)

        # 3. Save the raw audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        print(f"Raw audio saved to: {tmp_path}")

        # 4. Load and validate the audio file
        try:
            audio = AudioSegment.from_wav(tmp_path)
            print(f"Audio loaded successfully. Duration: {len(audio)} ms")

            # Check if the audio is too short
            if len(audio) < 500:  # Minimum 0.5 seconds
                await channel.send("❌ Recording too short to process")
                return

            # 5. Convert to Whisper-compatible format (16kHz, mono)
            print("Converting audio to 16kHz mono...")
            audio = audio.set_frame_rate(16000).set_channels(1)

            # 6. Save the processed audio to a new temporary file
            processed_temp_path = "processed_audio.wav"
            audio.export(processed_temp_path, format="wav")
            print(f"Processed audio saved to: {processed_temp_path}")

            # 7. Transcribe the processed audio
            transcription = audio_service.transcribe_audio(processed_temp_path)
            transcript = transcription.get("text", "No transcript available.")
            summary = meeting_service.generate_summary(transcript)
            mom = summary.get("summary", "No summary available.")

            # 8. Send the meeting minutes to the channel
            await channel.send(f"📝 **Meeting Minutes:**\n{mom}")

        except Exception as e:
            await channel.send(f"❌ Audio processing error: {str(e)}")
            print(f"Error processing audio: {e}")

    except Exception as e:
        await channel.send(f"❌ Critical error: {str(e)}")
        print(f"Critical error: {e}")

    finally:
        # Clean up temporary files
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if "processed_temp_path" in locals() and os.path.exists(processed_temp_path):
            os.remove(processed_temp_path)


# -------------------------------
# MOM GENERATION FROM AUDIO FILE UPLOAD
# -------------------------------
@bot.command()
async def mom_from_file(ctx):
    """Generates MoM from an uploaded .wav audio file."""
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a `.wav` audio file to the command!")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith(".wav"):
        await ctx.send("❌ Invalid file type. Please upload a `.wav` audio file.")
        return

    await ctx.send("⏳ Processing audio file, generating meeting minutes...")

    temp_audio_path = "uploaded_audio.wav"  # Temporary file for the uploaded audio

    try:
        audio_bytes = await attachment.read()
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        print(f"Uploaded audio file saved to: {temp_audio_path}")

        # Transcribe audio from the file path
        transcription = audio_service.transcribe_audio(temp_audio_path)
        transcript = transcription.get("text", "No transcript available.")
        summary = meeting_service.generate_summary(transcript)
        mom = summary.get("summary", "No summary available.")

        await ctx.send(f"📝 **Meeting Minutes from Uploaded File:**\n{mom}")

    except Exception as e:
        await ctx.send(f"❌ Error processing uploaded audio file: {str(e)}")
        print(f"Error processing uploaded audio file: {e}")

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


# -------------------------------
# RUN BOT
# -------------------------------
bot.run(os.getenv("TOKEN"))
