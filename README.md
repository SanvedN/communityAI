# Community AI Dashboard

The Community AI Dashboard is a comprehensive platform designed for professional organizations to facilitate robust audio processing and moderation services. This application enables users to record and analyze meeting audio for transcription, minutes generation (MoM), and actionable insights extraction, as well as to assess the appropriateness of various media types (text, images, audio, and video).

---

## Table of Contents

- [Objectives](#objectives)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [File Descriptions](#file-descriptions)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Dependencies](#dependencies)
- [License](#license)

---

## Objectives

The primary goal of this project is to streamline meeting management and content moderation within a professional environment. The application provides:

- **Meeting Audio Analysis:**
  - Transcription of recorded audio.
  - Generation of meeting summaries.
  - Extraction of actionable items.
- **Content Moderation:**
  - Assessment of text, images, audio, and video content for inappropriateness using a moderation service.

---

## Features

- **Live Audio Recording:**  
  Record audio directly from the browser using a custom HTML/JavaScript recorder (with a proof-of-concept implementation) and process it for transcription and minutes generation.

- **Audio File Upload:**  
  Support for uploading existing WAV files for analysis.

- **Meeting Minutes Generation (MoM):**  
  Integration with audio transcription and summarization services to generate detailed meeting summaries and key action items.

- **Multimodal Content Moderation:**  
  Analyze text, images, audio, and video files to determine content appropriateness.

- **Downloadable Reports:**  
  Export meeting summaries as text files for further review and record-keeping.

---

## Folder Structure

```
communityai/
├── app/
│   ├── core/               # Core functionalities and configurations.
│   ├── db/                 # Database models and session management.
│   ├── routers/            # API route definitions.
│   ├── schemas/            # Data validation schemas.
│   ├── services/           # Business logic and service layer.
│   │   ├── audio_service.py       # Audio processing and transcription.
│   │   ├── meeting_service.py     # Meeting summary generation and action item extraction.
│   │   └── moderation_service.py  # Content moderation services.
│   └── __init__.py         # Initializes the app package.
├── test_audio.py           # Demonstration of audio input handling and meeting analysis.
├── app.py                  # Main streamlit UI showcasing all the functionalities
├── test_moderation.py      # Demonstration of multimodal content moderation.
└── README.md               # Project documentation.
```

---

## File Descriptions

- **app/services/audio_service.py:**  
  Provides functionality for processing audio inputs and transcribing recorded or uploaded audio.

- **app/services/meeting_service.py:**  
  Contains business logic for generating meeting summaries and extracting key action items from the transcript.

- **app/services/moderation_service.py:**  
  Implements content moderation functionality for analyzing text, images, audio, and video to detect inappropriate content.

- **test_audio.py:**  
  A test script that demonstrates how to capture audio (both live and via file upload), transcribe it, and generate meeting summaries with actionable items.

- **test_moderation.py:**  
  A test script that demonstrates media moderation capabilities across different media types using the moderation service.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://your-repository-url/communityai.git
   cd communityai
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   Ensure all required dependencies are installed by running:

   ```bash
   pip install -r requirements.txt
   ```

   _Note: Verify that any custom packages (if applicable) and service dependencies are available in your Python environment._

---

## Usage

### Running the Application

To launch the Community AI Dashboard:

```bash
streamlit run app.py
```

This command will open a browser window with the dashboard, allowing you to choose between the Meeting Minutes Generator and the Content Moderation features.

### Features

- **Meeting Minutes (MoM):**
  - **Record Live Audio:** Use the browser-based recorder to capture meeting audio. After recording, click on "Process Recorded Audio" to transcribe the audio, generate a meeting summary, and extract action items.
  - **Upload Audio File:** Upload an existing WAV file and process it similarly to obtain transcription and MoM.
- **Content Moderation:**

  - Choose a media type (Text, Image, Audio, Video) and provide the corresponding input. The service will analyze the content and return a simple inappropriateness flag.

- **Download Reports:**
  - Download the complete meeting summary as a text file for further analysis or record-keeping.

---

## Testing

You can run the following test scripts to validate the functionality of individual services:

- **Audio Analysis:**

  ```bash
  python test_audio.py
  ```

- **Content Moderation:**

  ```bash
  python test_moderation.py
  ```

These scripts demonstrate the core functionalities and help ensure the services are integrated correctly.

---

## Dependencies

- **Python 3.8+**
- **Streamlit**
- **pyaudio** (if applicable for non-browser audio recording)
- **requests**
- **streamlit-components**
- Additional libraries as defined in your `requirements.txt` (ensure that all dependencies for the transcription, summarization, and moderation services are installed).

---

## License

_Include your project's license information here (e.g., MIT License, Apache License, etc.)._
