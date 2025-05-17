# Healthcare Customer Support AI Agents (CrewAI + Google Gemini)

This project provides a RESTful API for healthcare customer support, powered by CrewAI agents and Google Gemini LLM. It automates and augments common support scenarios such as appointment scheduling, prescription refills, lab results, insurance inquiries, and more.

## Features
- 10 healthcare support scenarios handled by specialized AI agents
- Uses Google Gemini API for intelligent, context-aware responses
- RESTful API built with Flask (Python)
- Easily extensible and modular

## Directory Structure
```
ai/
  app.py           # Flask API entry point
  agents.py        # CrewAI agent logic for each scenario
  requirements.txt # Python dependencies
  README.md        # Project documentation
```

## Setup Instructions
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Google Gemini API credentials** (see `agents.py` for integration points).
3. **Run the Flask app:**
   ```bash
   python app.py
   ```

## API Usage
- **Endpoint:** `POST /ai-agent`
- **Request Body:**
  ```json
  {
    "scenario": "appointment", // see list below
    "patient_id": "12345",
    "details": { ... } // scenario-specific fields
  }
  ```
- **Response:**
  ```json
  {
    "response": "...AI-generated reply..."
  }
  ```

## Supported Scenarios
| Scenario Key           | Description                                 |
|-----------------------|---------------------------------------------|
| appointment           | Appointment scheduling/rescheduling         |
| prescription          | Prescription refill assistance              |
| lab_results           | Lab test results inquiry                    |
| insurance             | Insurance coverage inquiry                  |
| symptom_checker       | Symptom checker and triage                  |
| followup_reminder     | Follow-up appointment reminder              |
| specialist_referral   | Specialist referral management              |
| emergency             | Emergency contact routing                   |
| mental_health         | Mental health support                       |
| feedback              | Patient feedback collection                 |

## Example Request
```bash
curl -X POST http://localhost:5000/ai-agent \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "appointment",
    "patient_id": "12345",
    "details": {"doctor": "Dr. Smith", "action": "reschedule"}
  }'
```

## Notes
- Integrate your Google Gemini API key and logic in `agents.py`.
- Extend or customize agent logic as needed for your healthcare use case. 