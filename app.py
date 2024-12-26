import streamlit as st
import requests
import pyaudio
import wave
import os

# Backend API Base URL
API_BASE_URL = "http://127.0.0.1:8000/api"

# Page Configuration
st.set_page_config(
    page_title="Community AI Dashboard",
    page_icon="🤖",
    layout="wide",
)

# Sidebar Menu
st.sidebar.title("Community AI")
menu = st.sidebar.selectbox(
    "Navigation", ["Home", "Meeting", "Moderation", "Login", "Signup"]
)

# Global State
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None


# Authentication Functions
def authenticate_user(email, password):
    url = f"{API_BASE_URL}/auth/login"
    data = {"username": email, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        st.session_state["auth_token"] = response.json()["access_token"]
        return True
    else:
        st.error("Login failed. Please check your credentials.")
        return False


def register_user(email, password):
    url = f"{API_BASE_URL}/auth/signup"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        st.success("Signup successful! Please log in.")
        return True
    else:
        st.error("Signup failed. Email might already be registered.")
        return False


# Headers with Token
def get_headers():
    return {"Authorization": f"Bearer {st.session_state['auth_token']}"}


# Home Page
if menu == "Home":
    st.title("Welcome to Community AI")
    st.write("Use this dashboard to manage meetings and moderate content.")

# Meeting Page
elif menu == "Meeting":
    st.title("Meeting Management")

    if st.session_state["auth_token"]:
        st.header("Record and Process Meeting Audio")

        def record_audio(output_filename, duration=5):
            st.info(f"Recording audio for {duration} seconds...")
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            frames = []

            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            wf = wave.open(output_filename, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

        if st.button("Start Recording and Process Audio"):
            audio_file = "recorded_audio.wav"
            record_audio(audio_file, duration=5)

            with open(audio_file, "rb") as f:
                files = {"audio": (audio_file, f, "audio/wav")}
                url = f"{API_BASE_URL}/meeting/record"
                headers = get_headers()
                response = requests.post(url, files=files, headers=headers)

            os.remove(audio_file)

            if response.status_code == 200:
                meeting_summary = response.json()
                st.success("Meeting processed successfully!")

                # Download Summary
                summary_text = f"Meeting Summary:\n{meeting_summary['summary']}\n\nDetails:\n{meeting_summary['details']}"
                st.download_button(
                    label="Download Summary",
                    data=summary_text,
                    file_name="meeting_summary.txt",
                    mime="text/plain",
                )
            else:
                st.error("Failed to process meeting audio.")
    else:
        st.warning("Please log in to access this feature.")

# Moderation Page
elif menu == "Moderation":
    st.title("Content Moderation")

    if st.session_state["auth_token"]:
        st.header("Upload and Analyze Content")

        file = st.file_uploader(
            "Upload a file (image, audio, video, or text)",
            type=["jpg", "jpeg", "png", "mp4", "wav", "txt"],
        )
        content_type = st.selectbox("Content Type", ["text", "image", "audio", "video"])

        if file and st.button("Analyze Content"):
            url = f"{API_BASE_URL}/moderation/"
            files = {"content": file}
            data = {"content_type": content_type}
            headers = get_headers()
            response = requests.post(url, files=files, data=data, headers=headers)

            if response.status_code == 200:
                analysis_results = response.json()
                st.success("Analysis Results:")
                st.json(analysis_results)
            else:
                st.error("Failed to analyze the content.")
    else:
        st.warning("Please log in to access this feature.")

# Login Page
elif menu == "Login":
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(email, password):
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your credentials.")

# Signup Page
elif menu == "Signup":
    st.title("Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        register_user(email, password)
