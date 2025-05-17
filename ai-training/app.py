from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from train import HealthcareSupportAI
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
flask_app = Flask(__name__)
CORS(flask_app, resources={r"/predict": {"origins": ["http://localhost:3000", "https://sympai-lac.vercel.app/dashboard"]}})
api = Api(flask_app)

# Initialize AI model
ai_model = HealthcareSupportAI()

# Initialize Gemini
try:
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    gemini_model = genai.GenerativeModel(os.getenv('GEMINI_MODEL'))
    print("Gemini model initialized successfully!")
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    print("Falling back to base model only")
    gemini_model = None

# Load trained model and data
try:
    ai_model.load_model('models')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please train the model first by running train.py")

# Load response templates and data
with open('datasets/healthcare_support_data.json', 'r') as f:
    healthcare_data = json.load(f)

# Add conversation patterns
conversation_patterns = {
    "greetings": {
        "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
        "responses": [
            "Hello! How can I assist you today?",
            "Hi there! What can I help you with?",
            "Welcome! How may I help you?"
        ]
    },
    "farewells": {
        "patterns": ["bye", "goodbye", "see you", "thanks", "thank you"],
        "responses": [
            "Goodbye! Take care!",
            "Thank you for chatting with me. Have a great day!",
            "You're welcome! Let me know if you need anything else."
        ]
    },
    "emergency": {
        "patterns": [
            "emergency", "severe pain", "chest pain", "difficulty breathing", 
            "heart attack", "stroke", "bleeding", "unconscious", "severe allergic",
            "critical", "urgent", "life-threatening", "immediate help"
        ],
        "response": "⚠️ This sounds like a medical emergency. Please call emergency services (911) immediately or go to the nearest emergency room. Do not wait for an online response."
    }
}

def check_emergency(query):
    """Check if the query indicates a medical emergency"""
    query_lower = query.lower()
    emergency_patterns = conversation_patterns["emergency"]["patterns"]
    
    if any(pattern in query_lower for pattern in emergency_patterns):
        return True, conversation_patterns["emergency"]["response"]
    return False, None

def is_general_conversation(query):
    """Check if the query is a general conversation starter"""
    query_lower = query.lower()
    
    # Check greetings and farewells
    for conv_type in ["greetings", "farewells"]:
        if any(pattern in query_lower for pattern in conversation_patterns[conv_type]["patterns"]):
            import random
            return True, random.choice(conversation_patterns[conv_type]["responses"])
    
    return False, None

def validate_template_data(template, data):
    """Check if all template placeholders have corresponding data"""
    placeholders = re.findall(r'\{([^}]+)\}', template)
    return all(key in data for key in placeholders)

def get_response_template(intent, query):
    """Get the appropriate response template and fill it with data"""
    # Check for emergency first
    is_emergency, emergency_response = check_emergency(query)
    if is_emergency:
        return emergency_response

    # Check for general conversation
    is_general, general_response = is_general_conversation(query)
    if is_general:
        return general_response

    for q in healthcare_data['queries']:
        if q['intent'] == intent:
            template = q['response_template']
            
            # For Tier 2 queries, return a template with placeholders
            if q.get('tier') == 2:
                # Create a sample response with placeholders
                if intent == 'insurance_claim_status':
                    return template.format(
                        claim_id="[CLAIM_ID]",
                        status="[STATUS]",
                        denial_reason="[DENIAL_REASON]"
                    )
                elif intent == 'specialist_referral':
                    return template.format(
                        specialist="[SPECIALIST_NAME]",
                        specialist_email="[SPECIALIST_EMAIL]"
                    )
                elif intent == 'medication_adjustment_request':
                    return template.format(
                        doctor="[DOCTOR_NAME]",
                        medication_name="[MEDICATION_NAME]",
                        dosage="[CURRENT_DOSAGE]"
                    )
                elif intent == 'appointment_issue_resolution':
                    return template.format(
                        doctor="[DOCTOR_NAME]",
                        date="[NEW_DATE]",
                        time="[NEW_TIME]"
                    )
                elif intent == 'lab_test_explanation':
                    return template.format(
                        test_name="[TEST_NAME]",
                        result="[TEST_RESULT]",
                        interpretation="[INTERPRETATION]",
                        condition="[CONDITION]",
                        doctor="[DOCTOR_NAME]"
                    )
                elif intent == 'insurance_eligibility_verification':
                    return template.format(
                        service="[SERVICE_NAME]",
                        insurance_provider="[INSURANCE_PROVIDER]"
                    )
            
            # Handle other intents as before
            if intent == 'doctor_availability':
                query_lower = query.lower()
                for doc in healthcare_data['data_sources']['doctors']:
                    # More flexible doctor name matching
                    doc_name_parts = doc['name'].lower().split()
                    if any(part in query_lower for part in doc_name_parts):
                        data = {
                            'doctor': doc['name'],
                            'availability': ', '.join(doc['availability']),
                            'time': doc['time'],
                            'room': doc['room']
                        }
                        if validate_template_data(template, data):
                            return template.format(**data)
                # No matching doctor found
                return "I couldn't find the doctor you're looking for. Here are our available doctors: " + ", ".join(doc['name'] for doc in healthcare_data['data_sources']['doctors'])
            
            elif intent == 'department_services':
                for dept in healthcare_data['data_sources']['departments']:
                    if dept['name'].lower() in query.lower():
                        data = {
                            'department': dept['name'],
                            'services': ', '.join(dept['services'])
                        }
                        if validate_template_data(template, data):
                            return template.format(**data)
                # No matching department found
                return "I couldn't find the department you're looking for. Here are our available departments: " + ", ".join(dept['name'] for dept in healthcare_data['data_sources']['departments'])
            
            elif intent == 'insurance_coverage':
                for ins in healthcare_data['data_sources']['insurance_partners']:
                    if ins['name'].lower() in query.lower():
                        data = {
                            'insurance_provider': ins['name'],
                            'services_covered': ', '.join(ins['services_covered']),
                            'contact': ins['contact']
                        }
                        if validate_template_data(template, data):
                            return template.format(**data)
                # No matching insurance found
                return "I couldn't find the insurance provider you mentioned. We work with: " + ", ".join(ins['name'] for ins in healthcare_data['data_sources']['insurance_partners'])
            
            elif intent == 'policy_inquiry':
                if 'cancel' in query.lower():
                    return healthcare_data['data_sources']['policies']['cancellation_policy']
                elif 'bill' in query.lower():
                    return healthcare_data['data_sources']['policies']['billing_policy']
                else:
                    return healthcare_data['data_sources']['policies']['data_privacy_policy']
            
            elif intent == 'medication_refill':
                return "To assist you with medication-related queries, I'll need to know: 1) The specific medication name, 2) When it was last prescribed, and 3) Your current symptoms or concerns. For your safety, please consult with your healthcare provider directly for medication-related issues."
    
    return None

def get_gemini_response(query, context=None):
    """Get enhanced response from Gemini"""
    if not gemini_model:
        return None
        
    try:
        prompt = f"""You are a medical AI assistant. Please provide a helpful response to the following query.
        Keep the response concise, professional, and focused on healthcare.
        
        Query: {query}
        
        {f'Context: {context}' if context else ''}
        
        Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def enhance_response(base_response, query, intent):
    """Enhance the base response with Gemini if available"""
    if not gemini_model:
        return base_response
        
    try:
        context = f"""
        Original Response: {base_response}
        Intent: {intent}
        
        Please enhance this response while keeping the core information. 
        Make it more natural and helpful, but keep it concise and professional.
        If the original response contains specific data (names, times, rooms, etc.), preserve that information exactly.
        """
        
        enhanced = get_gemini_response(query, context)
        return enhanced if enhanced else base_response
    except Exception as e:
        print(f"Error enhancing response: {e}")
        return base_response

class HealthQuery(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            if not data or 'query' not in data:
                return {'error': 'No query provided'}, 400
            
            query = data['query']
            
            # Check for emergency first
            is_emergency, emergency_response = check_emergency(query)
            if is_emergency:
                return {
                    'intent': 'emergency',
                    'confidence': 1.0,
                    'tier': 0,
                    'message': emergency_response,
                    'automated': True
                }

            # Check for general conversation
            is_general, general_response = is_general_conversation(query)
            if is_general:
                # Enhance general responses with Gemini
                enhanced_response = enhance_response(general_response, query, 'general_conversation')
                return {
                    'intent': 'general_conversation',
                    'confidence': 1.0,
                    'tier': 0,
                    'message': enhanced_response,
                    'automated': True
                }
                
            # Get intent prediction for other queries
            result = ai_model.predict(query)
            
            # Get base response template
            base_response = get_response_template(result['intent'], query)
            
            # Check query tier and adjust intent if needed
            query_lower = query.lower()
            
            # Keywords that indicate specific intents
            privacy_keywords = ["privacy", "data access", "unauthorized access", "data breach", "records accessed"]
            legal_keywords = ["legal", "lawyer", "attorney", "lawsuit", "sue", "legal action"]
            vip_keywords = ["priority", "immediate", "urgent consultation", "private consultation", "expedited"]
            clinical_trial_keywords = ["trial", "clinical trial", "research study", "experimental treatment"]
            hospice_keywords = ["hospice", "end of life", "palliative", "terminal care"]
            medication_interaction_keywords = ["drug interaction", "medicine interaction", "medication safety", "side effect"]
            
            # Adjust intent based on keywords
            if any(keyword in query_lower for keyword in privacy_keywords):
                result['intent'] = 'critical_data_privacy_violation'
                result['confidence'] = 0.95
            elif any(keyword in query_lower for keyword in legal_keywords):
                result['intent'] = 'legal_escalation'
                result['confidence'] = 0.95
            elif any(keyword in query_lower for keyword in vip_keywords):
                result['intent'] = 'VIP_patient_request'
                result['confidence'] = 0.95
            elif any(keyword in query_lower for keyword in clinical_trial_keywords):
                result['intent'] = 'clinical_trial_eligibility'
                result['confidence'] = 0.95
            elif any(keyword in query_lower for keyword in hospice_keywords):
                result['intent'] = 'end_of_life_care_support'
                result['confidence'] = 0.95
            elif any(keyword in query_lower for keyword in medication_interaction_keywords):
                result['intent'] = 'complex_medication_interaction'
                result['confidence'] = 0.95
            
            # Get the tier for the intent
            intent_tier = 0
            for q in healthcare_data['queries']:
                if q['intent'] == result['intent']:
                    intent_tier = q.get('tier', 0)
                    
                    if intent_tier == 4:
                        # Tier 4 - Critical/Legal/VIP cases
                        escalation_type = 'legal' if 'legal' in result['intent'] else 'VIP_support'
                        if 'end_of_life' in result['intent']:
                            escalation_type = 'VIP_support'  # Use VIP support for end-of-life care
                            
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 4,
                            'message': "This is a critical matter requiring immediate attention from our specialized team.",
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'escalation_contact': healthcare_data['data_sources']['escalation_contacts'].get(escalation_type),
                            'automated': False,
                            'priority': 'URGENT'
                        }
                    
                    elif intent_tier == 3:
                        # Tier 3 - Complex medical/privacy cases
                        escalation_type = 'compliance' if 'privacy' in result['intent'] else None
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 3,
                            'message': "This requires attention from our specialized medical team. A senior healthcare professional will review your case.",
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'escalation_contact': healthcare_data['data_sources']['escalation_contacts'].get(escalation_type),
                            'automated': False,
                            'priority': 'HIGH'
                        }
                    
                    elif intent_tier == 2:
                        # Tier 2 - Specialist intervention
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 2,
                            'message': "This query requires specialist assistance. A healthcare professional will review your request and respond shortly.",
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'automated': False
                        }
            
            # Handle Tier 0/1 queries
            if base_response:
                # Tier 0 - AI can handle
                enhanced_response = enhance_response(base_response, query, result['intent'])
                return {
                    'intent': result['intent'],
                    'confidence': result['confidence'],
                    'tier': 0,
                    'message': enhanced_response,
                    'automated': True
                }
            else:
                # Tier 1 - Basic human support needed
                suggested_response = f"I understand you have a question about {result['intent'].replace('_', ' ')}. " \
                                  f"To assist you better, I'll need more information. Could you please provide:\n" \
                                  f"1. Your specific concern or request\n" \
                                  f"2. Any relevant dates or times\n" \
                                  f"3. Any previous interactions related to this matter"
                
                return {
                    'intent': result['intent'],
                    'confidence': result['confidence'],
                    'tier': 1,
                    'message': "I apologize, but I'll need to transfer you to a human agent for better assistance with your query.",
                    'suggested_response': suggested_response,
                    'automated': False
                }
                
        except Exception as e:
            print(f"Error processing query: {e}")
            return {'error': 'Internal server error'}, 500

api.add_resource(HealthQuery, '/predict')

if __name__ == '__main__':
    flask_app.run(debug=True, port=5000) 