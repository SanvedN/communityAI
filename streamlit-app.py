import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from detoxify import Detoxify
import streamlit as st
from pydub import AudioSegment


# Function to convert video to audio and then to text
def video_to_text(video_path):
    try:
        video = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")
        text = audio_to_text(audio_path)
        return text
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return None
    finally:
        # Close the video file
        if "video" in locals():
            video.close()
        # Remove the temporary audio file if it exists
        if os.path.exists(audio_path):
            os.remove(audio_path)


# Function to convert audio to text
def audio_to_text(audio_path):
    temp_wav_path = None
    try:
        # Convert audio to WAV format if it's not already
        if not audio_path.lower().endswith(".wav"):
            audio = AudioSegment.from_file(audio_path)
            temp_wav_path = "temp_converted_audio.wav"
            audio.export(temp_wav_path, format="wav")
            audio_path = temp_wav_path

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition service"
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None
    finally:
        # Remove the temporary converted WAV file if it exists
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


# Function to classify text using Detoxify
def classify_text(text):
    detoxify_model = Detoxify("original")
    classification = detoxify_model.predict(text)
    return classification


# Streamlit UI
st.title("All-in-One Content Classifier")

# Add option for text input
text_input = st.text_area("Enter text to classify (optional)")

# File uploader
uploaded_file = st.file_uploader(
    "Or choose a file (audio, video, or text)",
    type=["mp4", "avi", "mov", "wav", "mp3", "m4a", "txt"],
)

if text_input or uploaded_file is not None:
    if text_input:
        text = text_input
    elif uploaded_file:
        temp_file_path = "temp_uploaded_file"
        try:
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_extension = uploaded_file.name.split(".")[-1].lower()

            if file_extension in ["mp4", "avi", "mov"]:
                st.write("Processing video file...")
                text = video_to_text(temp_file_path)
            elif file_extension in ["wav", "mp3", "m4a"]:
                st.write("Processing audio file...")
                text = audio_to_text(temp_file_path)
            elif file_extension == "txt":
                st.write("Processing text file...")
                with open(temp_file_path, "r") as file:
                    text = file.read()
            else:
                st.error(
                    "Unsupported file format. Please upload a video, audio, or text file."
                )
                text = None
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            text = None
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if text:
        st.write("Extracted or Entered Text:")
        st.write(text)
        classification = classify_text(text)
        st.write("Classification Results:")
        st.json(classification)
    elif text is None:
        st.warning(
            "Failed to process the input. Please try again or use a different file."
        )
