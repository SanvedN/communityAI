from detoxify import Detoxify
from .base_model import BaseModel

class DetoxifyModel(BaseModel):
    def __init__(self):
        self.model = Detoxify('original')

    def predict(self, text: str) -> dict:
        return self.model.predict(text)

    def train(self, train_data: list, val_data: list = None):
        # Detoxify doesn't support fine-tuning out of the box
        print("Training not implemented for pre-trained Detoxify model")

    def evaluate(self, test_data: list) -> dict:
        results = [self.predict(text) for text in test_data]
        # Implement evaluation metrics calculation here
        # We would not be needing accuracy scores as they are already given for the model in its documentation
    