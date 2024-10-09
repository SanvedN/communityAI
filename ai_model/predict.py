from .base_model import BaseModel
from .detoxify_model import DetoxifyModel
from .bert_model import BertModel
from .gemini_model import GeminiModel


class EnsembleModel(BaseModel):
    def __init__(self, gemini_api_key):
        self.models = [DetoxifyModel(), BertModel(), GeminiModel(gemini_api_key)]

    def predict(self, text: str) -> dict:
        predictions = [model.predict(text) for model in self.models]
        ensemble_toxicity = sum(pred["toxicity"] for pred in predictions) / len(
            predictions
        )
        return {"toxicity": ensemble_toxicity}

    def train(self, train_data: list, val_data: list = None):
        for model in self.models:
            model.train(train_data, val_data)

    def evaluate(self, test_data: list) -> dict:
        results = [self.predict(text) for text in test_data]
        # Implement evaluation metrics calculation here
        return {"accuracy": 0.0, "f1_score": 0.0}  # Placeholder