# Healthcare Support AI System

This is an AI-powered healthcare customer support system that handles Tier 0 and Tier 1 support queries. The system uses natural language processing and machine learning to understand and respond to customer inquiries about healthcare services.

## Features

- Intent classification for common healthcare queries
- Automatic handling of Tier 0 support requests
- Intelligent escalation to Tier 1 human support when needed
- REST API interface for easy integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Train the model:
```bash
python train.py
```

3. Start the API server:
```bash
python app.py
```

## API Usage

Send POST requests to `/predict` endpoint with JSON payload:

```json
{
    "query": "When is Dr. Miller available?"
}
```

Response format:
```json
{
    "intent": "doctor_availability",
    "confidence": 0.95,
    "tier": 0,
    "message": "Query can be handled automatically"
}
```

## Dataset

The system is trained on healthcare-specific data covering:
- Department services
- Doctor availability
- Insurance coverage
- Appointment management
- Lab results
- Policy inquiries
- Medication refills
- Test preparation

## Scaling the Dataset

To scale the dataset and improve the model:

1. Add more example queries to each intent in `datasets/healthcare_support_data.json`
2. Include more diverse response templates
3. Add new intents as needed
4. Retrain the model with the updated dataset

## Model Architecture

- Uses Sentence Transformers for text embedding
- Neural network with multiple dense layers
- Dropout layers for regularization
- Softmax output for intent classification

## Requirements

- Python 3.8+
- TensorFlow 2.13.0
- Sentence Transformers
- Flask
- Additional dependencies in requirements.txt 