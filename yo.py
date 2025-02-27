import torch
import whisper
import pyaudio
import numpy as np
import wave

# Load the Whisper Small model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device)

# List of inappropriate words to check
inappropriate_words = {
    "hate",
    "violence",
    "kill",
    "attack",
    "abuse",
    "racist",
    "curse",
    "offensive",
    "slur",
    "stupid",
    "idiot",
    "dumb",
    "moron",
    "loser",
    "shut up",
    "trash",
    "garbage",
    "fool",
    "disgusting",
    "ugly",
    "worthless",
    "bastard",
    "asshole",
    "douche",
    "bitch",
    "slut",
    "whore",
    "dick",
    "cock",
    "pussy",
    "fuck",
    "shit",
    "damn",
    "hell",
    "bullshit",
    "faggot",
    "retard",
    "cunt",
    "motherfucker",
    "son of a bitch",
    "prick",
    "wanker",
    "twat",
    "piss",
    "arse",
    "screw you",
    "jackass",
    "dipshit",
    "scumbag",
    "dumbass",
    "nigga",
    "nigger",
    "cracker",
    "chink",
    "spic",
    "wetback",
    "tranny",
    "homo",
    "dyke",
    "cocksucker",
    "redneck",
    "gook",
}


# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper works best with 16kHz
CHUNK = 4096  # Buffer size
RECORD_SECONDS = 3  # Process every 3 seconds

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a stream
stream = audio.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

print("Listening for speech... (Press Ctrl+C to stop)")

try:
    while True:
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        # Convert recorded frames to a numpy array
        audio_data = (
            np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        )  # Normalize

        # Transcribe the speech
        result = model.transcribe(audio_data)
        transcription = result["text"].strip()
        print(f"Transcribed: {transcription}")

        # Check for inappropriate words
        if any(word in transcription.lower() for word in inappropriate_words):
            print("⚠️ Warning: Inappropriate content detected!")

except KeyboardInterrupt:
    print("\nStopping transcription...")

finally:
    # Clean up resources
    stream.stop_stream()
    stream.close()
    audio.terminate()
