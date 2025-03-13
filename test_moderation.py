import os
import io
import wave
import shutil
import tempfile
import sounddevice as sd
import numpy as np
from app.services.moderation_service import ModerationService
from PIL import Image
import time  # Import time module for potential delays


def get_media_input_option():
    print("Choose an option for the media input:")
    print("1. Analyze text")
    print("2. Analyze image")
    print("3. Analyze audio")
    print("4. Analyze video")
    choice = input("Enter 1, 2, 3, or 4: ")
    return choice


def get_file_path(file_type: str):
    file_path = input(f"Enter the path to the {file_type} file: ").strip()
    if os.path.isfile(file_path):
        return file_path
    else:
        print(
            f"{file_type.capitalize()} file does not exist at the specified path: {file_path}"
        )
        return None


def analyze_text_input(moderation_service):
    text = input("Enter the text to analyze: ")
    if text:
        result = moderation_service.analyze_text(text)
        print("\n--- Text Analysis ---")
        print(result)


def analyze_image_input(moderation_service):
    image_path = get_file_path("image")
    if image_path:
        with Image.open(image_path) as image:
            result = moderation_service.analyze_image(image)
        print("\n--- Image Analysis ---")
        print(result)


def analyze_audio_input(moderation_service):
    audio_path = get_file_path("audio")
    if audio_path:
        with open(audio_path, "rb") as file:
            audio_data = file.read()
        result = moderation_service.analyze_audio(audio_data)
        print("\n--- Audio Analysis ---")
        print(result)


def analyze_video_input(moderation_service):
    video_path = get_file_path("video")
    if video_path:
        video_data = None  # Initialize video_data outside try block
        try:
            with open(video_path, "rb") as original_file:
                video_data = original_file.read()
        except Exception as e:
            print(f"Error initially reading video file: {e}")
            return  # Exit if we can't even read the file initially

        if video_data:  # Proceed only if video_data was successfully read
            try:
                result = moderation_service.analyze_video(video_data)
                print("\n--- Video Analysis ---")
                print(result)
            except Exception as e:
                print(f"Error analyzing video: {e}")


def main():
    moderation_service = ModerationService()
    choice = get_media_input_option()
    if choice == "1":
        analyze_text_input(moderation_service)
    elif choice == "2":
        analyze_image_input(moderation_service)
    elif choice == "3":
        analyze_audio_input(moderation_service)
    elif choice == "4":
        analyze_video_input(moderation_service)
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
