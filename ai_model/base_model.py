'''
This is the base model. It can be used as a reference to define methods for other models that we would be using.
'''

from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def predict(self, text: str) -> dict:
        """
        Predict the toxicity of the given text.
        
        Args:
            text (str): The input text to classify.
        
        Returns:
            dict: A dictionary containing toxicity scores.
        """
        pass

    @abstractmethod
    def train(self, train_data: list, val_data: list = None):
        """
        Train the model on the given data.
        
        Args:
            train_data (list): List of training examples.
            val_data (list, optional): List of validation examples.
        """
        pass

    @abstractmethod
    def evaluate(self, test_data: list) -> dict:
        """
        Evaluate the model on the given test data.
        
        Args:
            test_data (list): List of test examples.
        
        Returns:
            dict: A dictionary containing evaluation metrics.
        """
        pass