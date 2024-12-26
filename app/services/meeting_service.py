import google.generativeai as genai
from app.core.config import settings
from typing import Dict, List
import json


class MeetingService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_summary(self, transcript: str) -> Dict:
        prompt = f"""
        Please analyze this meeting transcript and provide:
        1. A concise summary
        2. Key action items
        3. Main discussion points
        4. Participants' contributions
        
        Transcript:
        {transcript}
        """

        response = self.model.generate_content(prompt)

        try:
            analysis = json.loads(response.text)
        except:
            # If response is not JSON, create structured format
            analysis = {
                "summary": response.text[:500],
                "action_items": [],
                "discussion_points": [],
                "participants": {},
            }

        return analysis

    def extract_action_items(self, transcript: str) -> List[Dict]:
        prompt = f"""
        Extract all action items from this meeting transcript.
        For each action item, identify:
        1. The action to be taken
        2. Who is responsible
        3. Any mentioned deadlines
        
        Transcript:
        {transcript}
        
        Return as JSON list.
        """

        response = self.model.generate_content(prompt)

        try:
            action_items = json.loads(response.text)
        except:
            action_items = []

        return action_items

    def analyze_participation(self, speaker_segments: List[Dict]) -> Dict:
        # Calculate speaking time and contributions per participant
        participation = {}

        for segment in speaker_segments:
            speaker = segment["speaker"]
            duration = segment["end_time"] - segment["start_time"]

            if speaker not in participation:
                participation[speaker] = {
                    "total_time": 0,
                    "speaking_turns": 0,
                    "segments": [],
                }

            participation[speaker]["total_time"] += duration
            participation[speaker]["speaking_turns"] += 1
            participation[speaker]["segments"].append(segment)

        return participation
