from flask import Flask, request, jsonify
# from agents import (
#     appointment_agent,
#     medical_report_agent
# )
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
genai.configure(api_key=GEMINI_API_KEY)

# Load JSON configurations
def load_json_file(filename):
    try:
        with open(f'datasets/{filename}', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

# Load configurations
TRAINING_DATASETS = load_json_file('healthcare_training.json')
PROMPT_TEMPLATES = load_json_file('prompt_templates.json')
TIER_DETECTION_RULES = {
    "appointment": {
        "tier1_triggers": {
            "keywords": [
                "urgent", "emergency", "asap", "critical",
                "must", "need", "important", "serious",
                "today", "immediately", "right away",
                "medical condition", "health issue",
                "pain", "severe", "worsening"
            ],
            "time_sensitivity": [
                "today", "tomorrow", "this week",
                "as soon as possible", "right away"
            ],
            "special_requirements": [
                "wheelchair", "interpreter", "accommodation",
                "special needs", "assistance", "help with"
            ],
            "escalation_phrases": [
                "speak to someone", "talk to someone",
                "not acceptable", "too long",
                "can't wait", "cannot wait",
                "supervisor", "manager",
                "complaint", "unhappy",
                "frustrated", "disappointed"
            ]
        }
    },
    "medical_report": {
        "tier1_triggers": {
            "keywords": [
                "worried", "concerned", "anxious",
                "abnormal", "unusual", "irregular",
                "high", "low", "elevated",
                "detailed", "specific", "exact",
                "meaning", "implications", "risks"
            ],
            "medical_terms": [
                "diagnosis", "prognosis", "treatment",
                "condition", "disease", "disorder",
                "chronic", "acute", "severe"
            ],
            "multiple_metrics": [
                "all results", "every result",
                "full report", "complete report",
                "all numbers", "all values",
                "everything", "all of them"
            ],
            "relationship_queries": [
                "related to", "connection between",
                "affect", "impact", "cause",
                "why", "how come", "reason for"
            ]
        }
    }
}

def detect_tier(scenario, messages, current_tier=0):
    """
    Automatically detect whether a request should be handled by Tier 0 or Tier 1.
    
    Args:
        scenario (str): The scenario type (appointment/medical_report)
        messages (list): List of conversation messages
        current_tier (int): Current tier level (default 0)
    
    Returns:
        int: Recommended tier level (0 or 1)
    """
    # If already at Tier 1, stay there
    if current_tier == 1:
        return 1

    # Get scenario-specific triggers
    triggers = TIER_DETECTION_RULES.get(scenario, {}).get("tier1_triggers", {})
    if not triggers:
        return 0

    # Get the last user message
    last_user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"].lower()
            break

    # Check message length - complex queries often need Tier 1
    if len(last_user_message.split()) > 20:
        return 1

    # Check for Tier 1 triggers in the last user message
    for category, keywords in triggers.items():
        for keyword in keywords:
            if keyword.lower() in last_user_message:
                return 1

    # Check conversation history for escalation patterns
    user_messages = [msg["content"].lower() for msg in messages if msg["role"] == "user"]
    
    # Multiple questions in conversation history suggest complexity
    if len(user_messages) >= 3:
        question_count = sum(1 for msg in user_messages if "?" in msg)
        if question_count >= 2:
            return 1

    # Repeated similar questions might indicate Tier 0 isn't sufficient
    if len(user_messages) >= 2:
        similar_questions = 0
        for i in range(len(user_messages) - 1):
            if any(word in user_messages[i+1] for word in user_messages[i].split() if len(word) > 4):
                similar_questions += 1
        if similar_questions >= 2:
            return 1

    return 0

def format_example(example, is_tier1=False):
    """Format a single example for inclusion in the prompt."""
    if is_tier1:
        return f"""User Request: {example['user']}
Previous Tier 0 Response: {example['previous_tier0']}
Assistant Response: {example['assistant']}
Why This Works: {example['explanation']}
Tags: {', '.join(example['tags'])}
---"""
    else:
        return f"""User Request: {example['user']}
Assistant Response: {example['assistant']}
Why This Works: {example['explanation']}
Tags: {', '.join(example['tags'])}
---"""

def build_prompt(scenario, tier, conversation, examples_text, tier0_response=None):
    """Build prompt using templates from JSON configuration."""
    template_config = PROMPT_TEMPLATES.get(scenario, {}).get(f"tier{tier}")
    if not template_config:
        return None

    # Convert capabilities and response format to string representation
    capabilities_str = "\n".join([f"- {cap}" for cap in template_config["capabilities"]])
    response_format_str = "\n".join([f"- {k}: {v}" for k, v in template_config["response_format"].items()])

    # Fill in the template
    return template_config["template"].format(
        system_role=template_config["system_role"],
        capabilities=capabilities_str,
        response_format=response_format_str,
        examples=examples_text,
        user_input=conversation,
        tier0_response=tier0_response or "None"
    )

# Modified Gemini direct endpoint to include automatic tier detection
@app.route('/gemini-direct', methods=['POST'])
def gemini_direct():
    data = request.get_json()
    scenario = data.get('scenario')
    messages = data.get('messages', [])
    
    # Automatically detect tier
    current_tier = data.get('tier', 0)
    detected_tier = detect_tier(scenario, messages, current_tier)
    
    # Get tier0_response if moving to Tier 1
    tier0_response = None
    if detected_tier == 1 and current_tier == 0:
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                tier0_response = msg["content"]
                break
    else:
        tier0_response = data.get('tier0_response')

    # Get training examples
    examples = TRAINING_DATASETS.get(scenario, {}).get(f"tier{detected_tier}_examples", [])
    examples_text = "\n\n".join([
        format_example(ex, is_tier1=(detected_tier == 1))
        for ex in examples
    ])

    # Build conversation history
    conversation = "\n".join([
        f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
        for msg in messages
    ])

    # Build prompt using template
    prompt = build_prompt(scenario, detected_tier, conversation, examples_text, tier0_response)
    if not prompt:
        return jsonify({"error": "Invalid scenario or tier"}), 400

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        response_data = {
            "response": response.text if hasattr(response, 'text') else str(response),
            "detected_tier": detected_tier,
            "tier_changed": detected_tier != current_tier
        }
        
        if hasattr(response, 'text'):
            return jsonify(response_data)
        elif hasattr(response, 'candidates') and response.candidates:
            response_data["response"] = response.candidates[0].text
            return jsonify(response_data)
        else:
            return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_appointment(data):
    return {"response": appointment_agent(data)}

def handle_medical_report(data):
    return {"response": medical_report_agent(data)}

SCENARIO_HANDLERS = {
    "appointment": handle_appointment,
    "medical_report": handle_medical_report
}

@app.route('/ai-agent', methods=['POST'])
def ai_agent():
    data = request.get_json()
    scenario = data.get('scenario')
    handler = SCENARIO_HANDLERS.get(scenario)
    if not handler:
        return jsonify({"error": "Unknown scenario."}), 400
    response = handler(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True) 