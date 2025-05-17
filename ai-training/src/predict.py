import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config.model_config import ModelConfig
import numpy as np

class HealthcareSupportPredictor:
    def __init__(self, model_path=None):
        self.config = ModelConfig()
        self.model_path = model_path or self.config.model_output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load model and tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()

        # Define confidence thresholds for different intents
        self.confidence_thresholds = {
            'schedule_appointment': 0.25,
            'interpret_report': 0.25,
            'general_inquiry': 0.25,
            'escalate_to_human': 0.2,
            'other': 0.25
        }

    def preprocess_conversation(self, messages):
        # Combine all messages with special focus on the last user message
        text = ""
        for msg in messages:
            role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
            text += role_prefix + msg['content'] + " [SEP] "
        
        # Add extra weight to the last user message if it exists
        last_user_msg = next((msg for msg in reversed(messages) if msg['role'] == 'user'), None)
        if last_user_msg:
            text += "User Query: " + last_user_msg['content']
        
        return text.strip()

    def predict(self, messages):
        # Preprocess conversation
        text = self.preprocess_conversation(messages)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            max_length=self.config.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1)
        
        # Get predicted intent and confidence
        predicted_intent = self.config.intent_labels[prediction.item()]
        confidence = probabilities[0][prediction.item()].item()
        
        # Check if confidence meets the threshold for the predicted intent
        threshold = self.confidence_thresholds.get(predicted_intent, 0.4)
        should_escalate = confidence < threshold
        
        # Always escalate if the message contains urgent keywords
        urgent_keywords = ['emergency', 'severe', 'urgent', 'pain', 'critical', 'bleeding', 'accident']
        last_user_msg = next((msg['content'].lower() for msg in reversed(messages) if msg['role'] == 'user'), "")
        if any(keyword in last_user_msg for keyword in urgent_keywords):
            predicted_intent = 'escalate_to_human'
            should_escalate = True
        
        return {
            'intent': predicted_intent,
            'confidence': confidence,
            'should_escalate': should_escalate or predicted_intent == 'escalate_to_human'
        }

def main():
    # Example usage
    predictor = HealthcareSupportPredictor()
    
    # Example conversation
    conversation = [
        {
            'role': 'user',
            'content': 'I need to schedule an appointment with Dr. Smith'
        },
        {
            'role': 'assistant',
            'content': 'I can help you with that. What time would you prefer?'
        },
        {
            'role': 'user',
            'content': 'Tomorrow afternoon if possible'
        }
    ]
    
    # Get prediction
    result = predictor.predict(conversation)
    print(f"Predicted Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Should Escalate: {result['should_escalate']}")

if __name__ == "__main__":
    main() 