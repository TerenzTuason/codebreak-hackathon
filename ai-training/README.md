# Healthcare Support AI System

This is an AI-powered healthcare customer support system that handles Tier 0 and Tier 1 support queries. The system uses natural language processing and machine learning to understand and respond to customer inquiries about healthcare services.

## Features

- Intent classification for common healthcare queries
- Automatic handling of Tier 0 support requests
- Intelligent escalation to Tier 1 human support when needed
- REST API interface for easy integration

## How the AI Flow Works (Simple Overview)

1. **User Query**: A user sends a question (like "When is Dr. Miller available?") to the API.
2. **Intent Detection**: The AI model analyzes the question to figure out what the user wants (the "intent"), such as asking about a doctor's schedule, insurance, or lab results.
3. **Data Lookup & Response**: The system looks up the answer in its healthcare data (doctors, departments, policies, etc.) and fills in a response template.
4. **AI Enhancement**: For more natural or complex answers, the system can use Google Gemini (a large language model) to improve the response.
5. **Emergency & Escalation**: If the question is urgent or the AI is unsure, it either gives an emergency message or asks a human for help (Tier 1 support).
6. **API Reply**: The system sends back a clear, helpful answer to the user.

## What Makes This Possible (Tech Stack)

- **Python**: Main programming language.
- **Flask**: Web server for the REST API.
- **PyTorch & Transformers**: For training and running the intent classification model.
- **Sentence Transformers**: To turn user questions into AI-friendly numbers (embeddings).
- **Google Gemini**: (Optional) For advanced, natural-sounding responses.
- **Datasets**: Custom healthcare data in JSON format for training and answering questions.
- **Other Libraries**: numpy, scikit-learn, flask-cors, flask-restful, and more (see requirements.txt).

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