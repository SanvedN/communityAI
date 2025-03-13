import os
from typing import List
import sys
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService


def get_audio_input_option():
    print("Choose an option for the audio input:")
    print("1. Record live audio")
    print("2. Use an existing audio file")
    choice = input("Enter 1 or 2: ")
    return choice


def record_audio_input(audio_service: AudioService, duration: int) -> str:
    filename = audio_service.generate_filename()
    print(f"Recording audio for {duration} seconds...")
    filepath = audio_service.record_audio(duration, filename)
    print(f"Audio recorded and saved as {filepath}")
    return filepath


def use_existing_audio_file() -> str:
    file_path = input("Enter the path to the audio file: ")
    if os.path.exists(file_path):
        print(f"Using existing audio file: {file_path}")
        return file_path
    else:
        print("File does not exist.")
        return None


def perform_analysis(
    audio_service: AudioService, meeting_service: MeetingService, audio_file: str
):
    # Step 1: Transcribe the audio
    with open(audio_file, "rb") as file:
        audio_data = file.read()

    print("Transcribing audio...")
    transcription = audio_service.transcribe_audio(audio_data)

    transcript_text = "\n".join([segment["text"] for segment in transcription])
    print("Transcription completed.")

    # Step 3: Analyze the meeting
    print("Analyzing meeting summary...")
    summary = meeting_service.generate_summary(transcript_text)
    print("Summary generated.")

    print("Extracting action items...")
    action_items = meeting_service.extract_action_items(transcript_text)
    print("Action items extracted.")

    # Output results
    print("\n--- Meeting Summary ---")
    print("Transcription: ", transcript_text)
    print("Summary:", summary["summary"])
    print("\n--- Action Items ---")
    for item in action_items:
        print(
            f"Action: {item.get('action')}, Responsible: {item.get('responsible')}, Deadline: {item.get('deadline')}"
        )


def main():
    audio_service = AudioService()
    meeting_service = MeetingService()

    # Get audio input choice
    choice = get_audio_input_option()

    # Record or use existing audio
    audio_file = None
    if choice == "1":
        # Record audio (e.g., 30 seconds)
        audio_file = record_audio_input(audio_service, duration=30)
    elif choice == "2":
        audio_file = use_existing_audio_file()

    if audio_file:
        # Perform analysis on the audio
        perform_analysis(audio_service, meeting_service, audio_file)
    else:
        print("No valid audio file selected, exiting.")


if __name__ == "__main__":
    main()
