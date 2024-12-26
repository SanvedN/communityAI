import uuid
import pyaudio
import whisper
import os
import wave
import io
from pydub import AudioSegment
from typing import List, Dict, Tuple


class AudioService:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.model = whisper.load_model("medium")  # Load the Whisper medium model
        self.audio_folder = "meeting_audio"

        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)

    def generate_filename(self):
        return str(uuid.uuid4()) + ".wav"

    def record_audio(self, duration: int, filename: str) -> str:
        p = pyaudio.PyAudio()

        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        frames = []

        for _ in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        filepath = os.path.join(self.audio_folder, filename)

        wf = wave.open(filepath, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        return filepath

    def merge_audio_streams(self, audio_files: List[str]) -> bytes:
        combined = AudioSegment.empty()
        for file in audio_files:
            segment = AudioSegment.from_file(file)
            combined += segment

        # Export as bytes
        audio_bytes = io.BytesIO()
        combined.export(audio_bytes, format="wav")

        return audio_bytes.getvalue()

    def transcribe_audio(self, audio_data: bytes) -> List[Dict]:
        temp_audio_path = "temp_audio.wav"

        with open(temp_audio_path, "wb") as temp_audio_file:
            temp_audio_file.write(audio_data)

        # Use Whisper to transcribe audio
        transcription_result = self.model.transcribe(temp_audio_path)

        os.remove(temp_audio_path)  # Clean up temporary file

        return transcription_result["segments"]  # Return transcription segments

    def detect_speakers(self, audio_data: bytes) -> List[Tuple[str, float, float]]:
        from pyannote.audio import Pipeline

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token="HF_ACCESS_TOKEN",
        )

        temp_file = "temp_audio.wav"
        with wave.open(temp_file, "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(pyaudio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(audio_data)

        diarization = pipeline(temp_file)

        os.remove(temp_file)

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append((speaker, turn.start, turn.end))

        return segments
