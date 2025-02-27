import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from io import BytesIO
import requests

# Import your service classes (ensure these are implemented without circular imports)
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService
from app.services.moderation_service import ModerationService


#############################################
# Helper function to extract transcript text
def get_transcript_text(transcription):
    if isinstance(transcription, dict) and "text" in transcription:
        return transcription["text"]
    elif isinstance(transcription, list):
        transcript_parts = [
            seg.get("text", "") for seg in transcription if seg.get("text")
        ]
        if transcript_parts:
            return "\n".join(transcript_parts)
    return "Transcript not available."


#############################################
# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Modal Meeting & Moderation Dashboard", layout="wide"
)
st.title("Multi-Modal Meeting & Moderation Dashboard")

# Sidebar Navigation
page = st.sidebar.selectbox("Choose a Feature", ["Meeting MoM", "Content Moderation"])

#############################################
# MEETING MINUTES (MoM) FUNCTIONALITY
#############################################
if page == "Meeting MoM":
    st.header("Meeting Minutes (MoM) Generation")
    meeting_option = st.radio(
        "Select Audio Input Method", ["Record Live Audio", "Upload Audio File"]
    )

    # Create service instances
    audio_service = AudioService()
    meeting_service = MeetingService()

    # -------------------------------
    # LIVE AUDIO RECORDING USING CUSTOM RECORDER
    # -------------------------------
    if meeting_option == "Record Live Audio":
        st.subheader("Record Audio using Browser Recorder")

        # HTML/JavaScript for recording audio
        recorder_html = """
        <html>
          <head>
            <script>
              var mediaRecorder;
              var recordedChunks = [];
              
              function startRecording() {
                  navigator.mediaDevices.getUserMedia({ audio: true })
                  .then(function(stream) {
                      mediaRecorder = new MediaRecorder(stream);
                      recordedChunks = [];
                      mediaRecorder.start();
                      mediaRecorder.ondataavailable = function(e) {
                        if (e.data.size > 0) {
                            recordedChunks.push(e.data);
                        }
                      };
                      mediaRecorder.onstop = function(e) {
                        var blob = new Blob(recordedChunks, { 'type' : 'audio/wav' });
                        var reader = new FileReader();
                        reader.readAsDataURL(blob); 
                        reader.onloadend = function() {
                            var base64data = reader.result;
                            const streamlitDoc = window.parent.document;
                            const inputElement = streamlitDoc.getElementById("audio-data");
                            if (inputElement) {
                                inputElement.value = base64data;
                                inputElement.dispatchEvent(new Event("change"));
                            }
                        }
                      };
                  });
              }
              
              function stopRecording() {
                  if(mediaRecorder) {
                      mediaRecorder.stop();
                  }
              }
            </script>
          </head>
          <body>
            <button onclick="startRecording()">Start Recording</button>
            <button onclick="stopRecording()">Stop Recording</button>
          </body>
        </html>
        """
        # Create a hidden text input to capture the audio Base64 data
        audio_data = st.text_input(
            "Recorded Audio (Base64)", key="audio-data", value="", type="default"
        )
        components.html(recorder_html, height=200)

        if st.button("Process Recorded Audio"):
            if not st.session_state.get("audio-data", audio_data) or audio_data == "":
                st.error(
                    "No audio recorded yet. Please record audio and then stop recording."
                )
            else:
                try:
                    # The audio_data string is in the format "data:audio/wav;base64,..."
                    header, encoded = st.session_state.get(
                        "audio-data", audio_data
                    ).split(",", 1)
                    audio_bytes = base64.b64decode(encoded)
                except Exception as e:
                    st.error(f"Error decoding audio data: {e}")
                    audio_bytes = None

                if audio_bytes:
                    # Save audio to a temporary WAV file
                    audio_filename = "recorded_meeting.wav"
                    with open(audio_filename, "wb") as f:
                        f.write(audio_bytes)

                    st.audio(audio_bytes, format="audio/wav")

                    # Process the audio file using your services
                    with open(audio_filename, "rb") as f:
                        audio_data_for_processing = f.read()
                    transcription = audio_service.transcribe_audio(
                        audio_data_for_processing
                    )
                    transcript_text = get_transcript_text(transcription)

                    try:
                        summary = meeting_service.generate_summary(transcript_text)
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                        summary = {
                            "summary": "Summary generation is currently unavailable."
                        }

                    action_items = meeting_service.extract_action_items(transcript_text)

                    st.subheader("Transcription")
                    st.text_area("Transcript", transcript_text, height=200)
                    summary_text = summary.get("summary", "No summary available.")
                    st.subheader("Meeting Summary")
                    st.text_area("Summary", value=summary_text, height=600)
                    st.download_button(
                        "Download Summary",
                        data=summary_text,
                        file_name="meeting_summary.txt",
                        mime="text/plain",
                    )

                    st.subheader("Action Items")
                    if action_items:
                        for item in action_items:
                            st.write(
                                f"- Action: {item.get('action')}, Responsible: {item.get('responsible')}, Deadline: {item.get('deadline')}"
                            )
                    else:
                        st.write("No action items found.")

                    os.remove(audio_filename)

    # -------------------------------
    # UPLOAD EXISTING AUDIO FILE
    # -------------------------------
    else:
        st.subheader("Upload Audio File")
        uploaded_audio = st.file_uploader(
            "Upload your audio file (wav format)", type=["wav"]
        )
        if uploaded_audio is not None:
            if st.button("Process Uploaded Audio"):
                audio_data = uploaded_audio.read()
                transcription = audio_service.transcribe_audio(audio_data)
                transcript_text = get_transcript_text(transcription)
                try:
                    summary = meeting_service.generate_summary(transcript_text)
                except Exception as e:
                    st.error(f"Error generating summary: {e}")
                    summary = {
                        "summary": "Summary generation is currently unavailable."
                    }
                action_items = meeting_service.extract_action_items(transcript_text)

                st.subheader("Transcription")
                st.text_area("Transcript", transcript_text, height=200)
                summary_text = summary.get("summary", "No summary available.")
                st.subheader("Meeting Summary")
                st.text_area("Summary", value=summary_text, height=600)
                st.download_button(
                    "Download Summary",
                    data=summary_text,
                    file_name="meeting_summary.txt",
                    mime="text/plain",
                )

                st.subheader("Action Items")
                if action_items:
                    for item in action_items:
                        st.write(
                            f"- Action: {item.get('action')}, Responsible: {item.get('responsible')}, Deadline: {item.get('deadline')}"
                        )
                else:
                    st.write("No action items found.")

#############################################
# CONTENT MODERATION FUNCTIONALITY
#############################################
elif page == "Content Moderation":
    st.header("Content Moderation")
    mod_option = st.selectbox(
        "Select Content Type", ["Text", "Image", "Audio", "Video"]
    )
    moderation_service = ModerationService()

    def filter_result(result, key="is_inappropriate"):
        return {key: result.get(key, False)}

    if mod_option == "Text":
        text_input = st.text_area("Enter text for moderation analysis")
        if st.button("Analyze Text"):
            if text_input:
                result = moderation_service.analyze_text(text_input)
                # filtered_result = filter_result(result)
                st.subheader("Text Moderation Results")
                st.json(result)
            else:
                st.error("Please enter text to analyze.")
    elif mod_option == "Image":
        uploaded_image = st.file_uploader(
            "Upload an image file", type=["jpg", "jpeg", "png"]
        )
        if st.button("Analyze Image"):
            if uploaded_image is not None:
                image_data = uploaded_image.read()
                result = moderation_service.analyze_image(image_data)
                # filtered_result = filter_result(result)
                st.subheader("Image Moderation Results")
                st.json(result)
            else:
                st.error("Please upload an image file.")
    elif mod_option == "Audio":
        uploaded_audio = st.file_uploader("Upload an audio file", type=["wav"])
        if st.button("Analyze Audio"):
            if uploaded_audio is not None:
                audio_data = uploaded_audio.read()
                result = moderation_service.analyze_audio(audio_data)
                # filtered_result = filter_result(result)
                st.subheader("Audio Moderation Results")
                st.json(result)
            else:
                st.error("Please upload an audio file.")
    elif mod_option == "Video":
        uploaded_video = st.file_uploader("Upload a video file", type=["mp4"])
        if st.button("Analyze Video"):
            if uploaded_video is not None:
                video_data = uploaded_video.read()
                result = moderation_service.analyze_video(video_data)
                if "is_inappropriate" in result:
                    filtered_result = {"is_inappropriate": result["is_inappropriate"]}
                else:
                    threshold = 0.5
                    filtered_result = {
                        "is_inappropriate": result.get("inappropriate_frame_ratio", 0)
                        > threshold
                    }
                st.subheader("Video Moderation Results")
                st.json(filtered_result)
            else:
                st.error("Please upload a video file.")
