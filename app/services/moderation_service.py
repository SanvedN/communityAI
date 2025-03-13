import cv2
import numpy as np
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import librosa
import io
import google.generativeai as genai
import soundfile as sf
import whisper
import random
import os
import tempfile
from moviepy.editor import VideoFileClip

# Initialize Google Gemini API (replace 'YOUR_GEMINI_API_KEY' with your actual key)
genai.configure(api_key="AIzaSyBDMYAX4pPgl0XO9wUwIEatNI3EdgHmYeU")


class ModerationService:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.toxicity_model = pipeline(
            "text-classification", model="unitary/toxic-bert", top_k=None
        )
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        self.whisper_model = whisper.load_model(
            "small"
        )  # Load Whisper model for transcription

    def analyze_text(self, text: str):
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        toxicity = self.toxicity_model(text)[0]
        is_inappropriate = any(score["score"] > 0.7 for score in toxicity)
        return {
            "sentiment": sentiment,
            "toxicity": toxicity,
            "is_inappropriate": is_inappropriate,
        }

    def analyze_image(self, image: Image):
        response = self.gemini_model.generate_content(
            [
                "Analyze this image and determine if it contains inappropriate content such as nudity, violence, or explicit material or anything that is NSFW (not safe for work) and cannot be posted on a group or community. Respond with 'yes' if inappropriate, otherwise 'no'.",
                image,
            ]
        )
        is_inappropriate = "yes" in response.text.lower()
        return {
            "is_inappropriate": is_inappropriate,
            "moderation_details": response.text,
        }

    def analyze_audio(self, audio_data: bytes):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            # Transcribe the audio using Whisper
            transcription_result = self.whisper_model.transcribe(temp_audio_path)
            transcribed_text = transcription_result.get("text", "")
            os.remove(temp_audio_path)  # Clean up temporary file

            # Perform text sentiment analysis on transcribed text
            text_analysis = self.analyze_text(transcribed_text)
            is_inappropriate = text_analysis["is_inappropriate"]
            return {
                "transcribed_text": transcribed_text,
                "analysis": text_analysis,
                "is_inappropriate": is_inappropriate,
            }
        except Exception as e:
            return {
                "error": f"Error analyzing audio: {e}",
                "is_inappropriate": False,
            }

    def analyze_video(self, video_data: bytes):
        try:
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_video_path = (
                temp_video.name
            )  # Get name *before* writing in case of issues
            try:  # Nested try to ensure temp_video is closed even if writing fails
                temp_video.write(video_data)
            finally:
                temp_video.close()  # Close file after writing

            # Extract frames from video
            clip = VideoFileClip(temp_video_path)
            duration = clip.duration
            frame_times = [
                random.uniform(0, duration) for _ in range(5)
            ]  # Select 5 random frames
            frames = [clip.get_frame(t) for t in frame_times]

            # Convert frames to PIL images and analyze
            frame_analysis_results = []
            inappropriate_frames = 0
            for frame in frames:
                image = Image.fromarray(frame)
                result = self.analyze_image(image)
                frame_analysis_results.append(result)
                if result["is_inappropriate"]:
                    inappropriate_frames += 1

            is_inappropriate = (
                inappropriate_frames > 0
            )  # If more any frame is inappropriate

            clip.close()  # Explicitly close the VideoFileClip to release resources!
            os.remove(temp_video_path)  # Clean up temporary file AFTER MoviePy is done!

            return {
                "frame_analysis": frame_analysis_results,
                "is_inappropriate": is_inappropriate,
            }
        except Exception as e:
            return {
                "error": f"Error analyzing video: {e}",
                "is_inappropriate": False,
            }
