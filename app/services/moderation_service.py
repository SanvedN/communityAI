import cv2
import numpy as np
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from nudenet import NudeDetector
import imagehash
import librosa
from typing import Dict, Union, Tuple
import io


class ModerationService:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.toxicity_model = pipeline(
            "text-classification", model="unitary/toxic-bert", top_k=None
        )

        self.nude_detector = NudeDetector()

    def analyze_text(self, text: str) -> Dict:
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.polarity_scores(text)

        # Toxicity detection
        toxicity = self.toxicity_model(text)[0]

        # AI text detection using basic heuristics
        ai_indicators = self.detect_ai_text(text)

        return {
            "sentiment": sentiment,
            "toxicity": toxicity,
            "is_ai_generated": ai_indicators > 0.7,
            "is_inappropriate": any(score["score"] > 0.7 for score in toxicity),
        }

    def analyze_image(self, image_data: bytes) -> Dict:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Calculate image hash for AI detection
        img_hash = str(imagehash.average_hash(image))

        # NSFW detection
        nsfw_result = self.nude_detector.detect(image)

        # Manipulation detection
        manipulation_score = self.detect_image_manipulation(image)

        return {
            "is_inappropriate": any(cls["score"] > 0.7 for cls in nsfw_result),
            "is_ai_generated": self.detect_ai_image(image),
            "manipulation_score": manipulation_score,
            "nsfw_details": nsfw_result,
        }

    def analyze_audio(self, audio_data: bytes) -> Dict:
        # Load audio
        y, sr = librosa.load(io.BytesIO(audio_data))

        # Extract features
        mfccs = librosa.feature.mfcc(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

        # Detect AI generation (basic features based)
        ai_score = self.detect_ai_audio(mfccs, spectral_rolloff)

        return {
            "is_ai_generated": ai_score > 0.7,
            "audio_features": {
                "mfccs_mean": np.mean(mfccs),
                "spectral_rolloff_mean": np.mean(spectral_rolloff),
            },
        }

    def analyze_video(self, video_data: bytes) -> Dict:
        temp_path = "temp_video.mp4"
        with open(temp_path, "wb") as f:
            f.write(video_data)

        cap = cv2.VideoCapture(temp_path)
        frames_analyzed = 0
        inappropriate_frames = 0
        ai_generated_frames = 0

        while cap.isOpened() and frames_analyzed < 100:  # Analyze up to 100 frames
            ret, frame = cap.read()
            if not ret:
                break

            if frames_analyzed % 10 == 0:  # Analyze every 10th frame
                pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                frame_analysis = self.analyze_image(pil_frame)

                if frame_analysis["is_inappropriate"]:
                    inappropriate_frames += 1
                if frame_analysis["is_ai_generated"]:
                    ai_generated_frames += 1

            frames_analyzed += 1

        cap.release()
        import os

        os.remove(temp_path)

        total_analyzed = frames_analyzed // 10
        return {
            "is_inappropriate": inappropriate_frames / total_analyzed > 0.3,
            "is_ai_generated": ai_generated_frames / total_analyzed > 0.7,
            "inappropriate_frame_ratio": inappropriate_frames / total_analyzed,
            "ai_generated_frame_ratio": ai_generated_frames / total_analyzed,
        }

    def detect_ai_text(self, text: str) -> float:
        indicators = [
            len(text.split()) > 100,  # Length
            len(set(text.split())) / len(text.split()) < 0.6,  # Vocabulary diversity
            text.count(".") / len(text.split()) > 0.1,  # Sentence structure
            any(
                phrase in text.lower() for phrase in ["as an ai", "as a language model"]
            ),  # Common AI phrases
        ]
        return sum(indicators) / len(indicators)

    def detect_ai_image(self, image: Image) -> bool:
        img_array = np.array(image)
        symmetric = self.check_symmetry(img_array)
        artifact_score = self.check_artifacts(img_array)
        consistency_score = self.check_pixel_consistency(img_array)

        return (symmetric and artifact_score > 0.7) or consistency_score > 0.8

    def detect_ai_audio(self, mfccs: np.ndarray, spectral_rolloff: np.ndarray) -> float:
        mfcc_std = np.std(mfccs)
        rolloff_std = np.std(spectral_rolloff)

        score = 0.6 * (mfcc_std < 0.5) + 0.4 * (  # Weight for MFCC variation
            rolloff_std < 0.5
        )  # Weight for spectral rolloff
        return score

    def check_symmetry(self, img_array: np.ndarray) -> bool:
        height, width = img_array.shape[:2]
        left = img_array[:, : width // 2]
        right = np.fliplr(img_array[:, width // 2 :])
        return np.mean(np.abs(left - right)) < 50

    def check_artifacts(self, img_array: np.ndarray) -> float:
        edges = cv2.Canny(img_array, 100, 200)
        return np.mean(edges) / 255

    def check_pixel_consistency(self, img_array: np.ndarray) -> float:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        glcm = self.get_glcm(gray)
        return np.mean(glcm)

    def get_glcm(
        self, img: np.ndarray, distance: int = 1, angle: int = 0
    ) -> np.ndarray:
        h, w = img.shape
        glcm = np.zeros((256, 256))

        # Horizontal GLCM
        for i in range(h):
            for j in range(w - distance):
                i1 = img[i, j]
                i2 = img[i, j + distance]
                glcm[i1, i2] += 1

        return glcm / glcm.sum()

    def detect_image_manipulation(self, image: Image) -> float:
        # Convert to numpy array
        img_array = np.array(image)

        # Error Level Analysis
        ela_score = self.error_level_analysis(img_array)

        # Noise analysis
        noise_score = self.analyze_noise_pattern(img_array)

        return (ela_score + noise_score) / 2

    def error_level_analysis(self, img_array: np.ndarray) -> float:
        # Save as JPEG with quality 90
        _, encoded = cv2.imencode(".jpg", img_array, [cv2.IMWRITE_JPEG_QUALITY, 90])
        decoded = cv2.imdecode(encoded, 1)

        # Calculate difference
        diff = np.abs(img_array - decoded)
        return np.mean(diff) / 255

    def analyze_noise_pattern(self, img_array: np.ndarray) -> float:
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)

        # Calculate noise pattern
        noise = np.abs(gray - denoised)

        # Check uniformity of noise
        return np.std(noise) / np.mean(noise) if np.mean(noise) > 0 else 0
