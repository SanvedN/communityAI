import google.generative.ai as genai
from .base_model import BaseModel


class GeminiModel(BaseModel):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def predict(self, text: str) -> dict:
        prompt = f"""
        Analyze the following text for toxicity. 
        Provide a toxicity score between 0 and 1, where 0 is not toxic at all and 1 is extremely toxic.
        Only respond with the numeric score, nothing else.

        Text: {text}

        Toxicity score:
        """

        response = self.model.generate_content(prompt)

        try:
            toxicity_score = float(response.text.strip())
            # Ensure the score is between 0 and 1
            toxicity_score = max(0, min(toxicity_score, 1))
        except ValueError:
            # If we can't convert the response to a float, default to 0.5
            toxicity_score = 0.5

        return {"toxicity": toxicity_score}

    def train(self, train_data: list, val_data: list = None):
        # Gemini doesn't support fine-tuning through this API
        print("Training not implemented for Gemini model")

    def evaluate(self, test_data: list) -> dict:
        results = [self.predict(text) for text in test_data]
        return results
