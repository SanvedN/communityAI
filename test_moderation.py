import os
from typing import Optional
import io
from app.services.moderation_service import ModerationService


def get_media_input_option():
    print("Choose an option for the media input:")
    print("1. Analyze text")
    print("2. Analyze image")
    print("3. Analyze audio")
    print("4. Analyze video")
    choice = input("Enter 1, 2, 3, or 4: ")
    return choice


def get_file_path(file_type: str) -> Optional[str]:
    file_path = input(f"Enter the path to the {file_type} file: ").strip()

    # Remove extra quotes if present (if user adds them by mistake)
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]

    # Debugging output
    print(f"Debug: Checking if file exists at path: {file_path}")

    if os.path.isfile(file_path):
        return file_path
    else:
        print(
            f"{file_type.capitalize()} file does not exist at the specified path: {file_path}"
        )
        return None


def analyze_text_input(moderation_service: ModerationService):
    text = input("Enter the text to analyze: ")
    analysis_result = moderation_service.analyze_text(text)
    print("\n--- Text Analysis ---")
    print(f"Sentiment: {analysis_result['sentiment']}")
    print(f"Toxicity: {analysis_result['toxicity']}")
    print(f"AI Generated: {analysis_result['is_ai_generated']}")
    print(f"Inappropriate: {analysis_result['is_inappropriate']}")


def analyze_image_input(moderation_service: ModerationService):
    image_path = get_file_path("image")
    if image_path:
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
            analysis_result = moderation_service.analyze_image(image_data)
            print("\n--- Image Analysis ---")
            print(f"Inappropriate: {analysis_result['is_inappropriate']}")
            print(f"AI Generated: {analysis_result['is_ai_generated']}")
            print(f"Manipulation Score: {analysis_result['manipulation_score']}")
            print(f"NSFW Details: {analysis_result['nsfw_details']}")


def analyze_audio_input(moderation_service: ModerationService):
    audio_path = get_file_path("audio")
    if audio_path:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
            analysis_result = moderation_service.analyze_audio(audio_data)
            print("\n--- Audio Analysis ---")
            print(f"AI Generated: {analysis_result['is_ai_generated']}")
            print(f"MFCCs Mean: {analysis_result['audio_features']['mfccs_mean']}")
            print(
                f"Spectral Rolloff Mean: {analysis_result['audio_features']['spectral_rolloff_mean']}"
            )


def analyze_video_input(moderation_service: ModerationService):
    video_path = get_file_path("video")
    if video_path:
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()
            analysis_result = moderation_service.analyze_video(video_data)
            print("\n--- Video Analysis ---")
            print(
                f"Inappropriate Frame Ratio: {analysis_result['inappropriate_frame_ratio']}"
            )
            print(
                f"AI Generated Frame Ratio: {analysis_result['ai_generated_frame_ratio']}"
            )


def main():
    moderation_service = ModerationService()

    # Get media input option
    choice = get_media_input_option()

    # Analyze based on the user's choice
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
