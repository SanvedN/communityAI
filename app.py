import os
from typing import Optional
import io
import streamlit as st
import sounddevice as sd
import numpy as np
import queue
import wave
from app.services.moderation_service import ModerationService
from app.services.meeting_service import MeetingService
from PIL import Image
import google.generativeai as genai
import tempfile
import random
from moviepy.editor import VideoFileClip

# Initialize services
moderation_service = ModerationService()
meeting_service = MeetingService()


def get_file_path(file_type: str) -> Optional[str]:
    file_path = input(f"Enter the path to the {file_type} file: ").strip()
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    if os.path.isfile(file_path):
        return file_path
    else:
        print(
            f"{file_type.capitalize()} file does not exist at the specified path: {file_path}"
        )
        return None


def analyze_text_input():
    text = st.text_area("Enter the text to analyze")
    if st.button("Analyze Text") and text:
        analysis_result = moderation_service.analyze_text(text)
        st.json(analysis_result)
    else:
        st.warning("Please enter text to analyze.")


def analyze_image_input():
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image and st.button("Analyze Image"):
        try:
            image = Image.open(uploaded_image)
            analysis_result = moderation_service.analyze_image(image)
            st.json(analysis_result)
        except Exception as e:
            st.error(f"Error processing image: {e}")
    else:
        st.warning("Please upload an image file.")


def analyze_audio_input():
    uploaded_audio = st.file_uploader("Upload an audio file", type=["wav"])
    if uploaded_audio and st.button("Analyze Audio"):
        try:
            audio_data = uploaded_audio.read()
            analysis_result = moderation_service.analyze_audio(audio_data)
            st.json(analysis_result)
        except Exception as e:
            st.error(f"Error processing audio: {e}")
    else:
        st.warning("Please upload an audio file.")


def analyze_video_input():
    uploaded_video = st.file_uploader("Upload a video file", type=["mp4"])
    if uploaded_video and st.button("Analyze Video"):
        try:
            video_data = uploaded_video.read()
            analysis_result = moderation_service.analyze_video(video_data)
            analysis_result.setdefault("frame_analysis", [])  # Ensure key exists
            st.json(analysis_result)
        except Exception as e:
            st.error(f"Error analyzing video: {e}")
    else:
        st.warning("Please upload a video file.")


# Live Audio Recording & Real-Time Analysis
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


def start_live_audio():
    st.write("Recording Live Audio... Speak now!")
    duration = 30  # Record for 30 seconds
    samplerate = 16000
    channels = 1
    audio_data = []

    with sd.InputStream(
        samplerate=samplerate, channels=channels, callback=audio_callback
    ):
        for _ in range(int(samplerate / 1024 * duration)):
            data = audio_queue.get()
            audio_data.append(data)

    audio_array = np.concatenate(audio_data, axis=0)
    audio_bytes = io.BytesIO()
    with wave.open(audio_bytes, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_array.tobytes())

    st.write("Processing Live Audio...")
    analysis_result = moderation_service.analyze_audio(audio_bytes.getvalue())
    st.json(analysis_result)

    if analysis_result.get("is_inappropriate", False):
        st.error("⚠️ Inappropriate content detected in speech!")

    transcript_text = analysis_result.get("transcribed_text", "")
    summary = meeting_service.generate_summary(transcript_text)
    action_items = meeting_service.extract_action_items(transcript_text)

    st.subheader("Meeting Summary")
    st.json(summary)
    st.subheader("Action Items")
    st.json(action_items)


st.title("Real-Time Moderation & Meeting Assistant")

option = st.sidebar.radio(
    "Select Feature",
    [
        "Text Moderation",
        "Image Moderation",
        "Audio Moderation",
        "Video Moderation",
        "Live Audio Recording",
    ],
)

if option == "Text Moderation":
    analyze_text_input()
elif option == "Image Moderation":
    analyze_image_input()
elif option == "Audio Moderation":
    analyze_audio_input()
elif option == "Video Moderation":
    analyze_video_input()
elif option == "Live Audio Recording":
    if st.button("Start Live Recording"):
        start_live_audio()
