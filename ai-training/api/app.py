from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
flask_app = Flask(__name__)
CORS(flask_app, resources={
    r"/predict": {
        "origins": ["http://localhost:3000", "https://sympai-lac.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
api = Api(flask_app)

# Initialize Gemini
try:
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    gemini_model = genai.GenerativeModel(os.getenv('GEMINI_MODEL'))
    print("Gemini model initialized successfully!")
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    print("Falling back to base model only")
    gemini_model = None

# Load response templates and data
try:
    with open('datasets/healthcare_support_data.json', 'r') as f:
        healthcare_data = json.load(f)
except Exception as e:
    print(f"Error loading healthcare data: {e}")
    # Provide minimal fallback data
    healthcare_data = {
        "queries": [],
        "data_sources": {
            "departments": [],
            "doctors": [],
            "insurance_partners": [],
            "policies": {
                "cancellation_policy": "Please contact support for policy information.",
                "billing_policy": "Please contact support for billing information.",
                "data_privacy_policy": "Please contact support for privacy information."
            }
        }
    }

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

def get_intent(query):
    """Simple rule-based intent detection for serverless deployment"""
    query_lower = query.lower()
    
    # Define intent patterns
    intent_patterns = {
        'doctor_availability': ['available', 'schedule', 'appointment', 'when can i see', 'booking'],
        'department_services': ['services', 'treatments', 'what does', 'offer', 'facilities'],
        'insurance_coverage': ['insurance', 'cover', 'policy', 'covered by'],
        'specialist_referral': ['referral', 'specialist', 'refer me to'],
        'medication_refill': ['refill', 'prescription', 'medicine', 'medication'],
        'test_preparation': ['prepare', 'preparation', 'ready for test', 'before test'],
        'lab_results': ['results', 'test results', 'lab report', 'blood test'],
        'policy_inquiry': ['policy', 'policies', 'rules', 'guidelines']
    }
    
    # Check each intent pattern
    for intent, patterns in intent_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            return {
                'intent': intent,
                'confidence': 0.8  # Simplified confidence score
            }
    
    # Default intent
    return {
        'intent': 'general_inquiry',
        'confidence': 0.6
    }

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
            
            # Handle specialist referral with actual doctor data
            if intent == 'specialist_referral':
                # Extract the requested specialty from the query
                specialties = {
                    'neurologist': 'Neurology',
                    'cardiologist': 'Cardiology',
                    'pediatrician': 'Pediatrics',
                    'orthopedist': 'Orthopedics'
                }
                
                requested_specialty = None
                query_lower = query.lower()
                for specialty_term, department in specialties.items():
                    if specialty_term in query_lower:
                        requested_specialty = department
                        break
                
                if not requested_specialty:
                    # If specialty not found in query, provide department list
                    available_departments = [dept['name'] for dept in healthcare_data['data_sources']['departments']]
                    return f"I can help you with referrals to these specialties: {', '.join(available_departments)}. Which specialist would you like to see?"
                
                # Find doctors in the requested specialty
                specialists = [
                    doc for doc in healthcare_data['data_sources']['doctors']
                    if doc['department'] == requested_specialty
                ]
                
                if not specialists:
                    return f"I apologize, but I couldn't find any {requested_specialty.lower()} specialists available at the moment. Would you like to check other specialties?"
                
                # Get the first available specialist
                specialist = specialists[0]
                specialist_email = f"{specialist['name'].lower().replace(' ', '.')}@citycarehospital.com"
                
                # Create a more informative response
                response = template.format(
                    specialist=specialist['name'],
                    specialist_email=specialist_email
                )
                
                # Add availability information
                response += f"\n\nDr. {specialist['name'].split()[-1]} is available on {', '.join(specialist['availability'])} from {specialist['time']} in room {specialist['room']}."
                
                return response
            
            # For other Tier 2 queries, keep existing placeholder handling
            elif q.get('tier') == 2:
                if intent == 'insurance_claim_status':
                    return template.format(
                        claim_id="[CLAIM_ID]",
                        status="[STATUS]",
                        denial_reason="[DENIAL_REASON]"
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
                        return template.format(**data)
                # No matching department found
                return "I couldn't find the department you're looking for. Here are our available departments: " + ", ".join(dept['name'] for dep in healthcare_data['data_sources']['departments'])
            
            elif intent == 'insurance_coverage':
                for ins in healthcare_data['data_sources']['insurance_partners']:
                    if ins['name'].lower() in query.lower():
                        data = {
                            'insurance_provider': ins['name'],
                            'services_covered': ', '.join(ins['services_covered']),
                            'contact': ins['contact']
                        }
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
        # Create a more detailed prompt that includes medical context
        prompt = f"""You are a medical AI assistant trained to provide accurate, helpful healthcare information. 
        Please provide a clear, professional response to the following medical query.
        
        Important guidelines:
        - Provide accurate medical information while being empathetic
        - If the query involves emergency symptoms, always advise seeking immediate medical attention
        - Include relevant medical terminology when appropriate
        - Keep responses concise but informative
        - If specific medical data is provided in the context, incorporate it accurately
        
        Query: {query}
        
        {f'Additional Context: {context}' if context else ''}
        
        Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def enhance_response(base_response, query, intent):
    """Enhanced response generation prioritizing Gemini"""
    if not gemini_model:
        return base_response
        
    try:
        # First, get specific data from our healthcare dataset
        specific_data = ""
        if intent == 'doctor_availability':
            for doc in healthcare_data['data_sources']['doctors']:
                if doc['name'].lower() in query.lower():
                    specific_data = f"Doctor {doc['name']} is available on {', '.join(doc['availability'])} at {doc['time']} in room {doc['room']}."
        elif intent == 'department_services':
            for dept in healthcare_data['data_sources']['departments']:
                if dept['name'].lower() in query.lower():
                    specific_data = f"The {dept['name']} department offers: {', '.join(dept['services'])}."
        elif intent == 'insurance_coverage':
            for ins in healthcare_data['data_sources']['insurance_partners']:
                if ins['name'].lower() in query.lower():
                    specific_data = f"{ins['name']} covers: {', '.join(ins['services_covered'])}. Contact: {ins['contact']}"
        
        # Create context combining our specific data and base response
        context = f"""
        Specific Healthcare Information: {specific_data if specific_data else 'No specific data available'}
        
        Base System Response: {base_response if base_response else 'No base response available'}
        
        Please incorporate any specific healthcare data (if available) into your response while providing comprehensive medical information.
        """
        
        # Get enhanced response from Gemini
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
                # Even for emergencies, get enhanced response while maintaining urgency
                emergency_context = "This is a MEDICAL EMERGENCY. Response must emphasize immediate medical attention while providing crucial first-aid information if applicable."
                enhanced_emergency = get_gemini_response(query, emergency_context) or emergency_response
                return {
                    'intent': 'emergency',
                    'confidence': 1.0,
                    'tier': 0,
                    'message': enhanced_emergency,
                    'automated': True
                }

            # Check for general conversation
            is_general, general_response = is_general_conversation(query)
            if is_general:
                enhanced_response = enhance_response(general_response, query, 'general_conversation')
                return {
                    'intent': 'general_conversation',
                    'confidence': 1.0,
                    'tier': 0,
                    'message': enhanced_response,
                    'automated': True
                }
                
            # Get intent prediction
            result = get_intent(query)
            
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
                            escalation_type = 'VIP_support'
                        
                        # Get enhanced response even for Tier 4
                        enhanced = enhance_response(
                            "This is a critical matter requiring immediate attention from our specialized team.",
                            query,
                            result['intent']
                        )
                        
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 4,
                            'message': enhanced,
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'escalation_contact': healthcare_data['data_sources']['escalation_contacts'].get(escalation_type),
                            'automated': False,
                            'priority': 'URGENT'
                        }
                    
                    elif intent_tier == 3:
                        # Tier 3 - Complex medical/privacy cases
                        escalation_type = 'compliance' if 'privacy' in result['intent'] else None
                        enhanced = enhance_response(
                            "This requires attention from our specialized medical team.",
                            query,
                            result['intent']
                        )
                        
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 3,
                            'message': enhanced,
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'escalation_contact': healthcare_data['data_sources']['escalation_contacts'].get(escalation_type),
                            'automated': False,
                            'priority': 'HIGH'
                        }
                    
                    elif intent_tier == 2:
                        # Tier 2 - Specialist intervention
                        enhanced = enhance_response(
                            base_response,
                            query,
                            result['intent']
                        )
                        
                        return {
                            'intent': result['intent'],
                            'confidence': result['confidence'],
                            'tier': 2,
                            'message': enhanced,
                            'suggested_response': base_response,
                            'required_data': q.get('required_data', []),
                            'automated': False
                        }
            
            # Handle Tier 0/1 queries - Always get enhanced response
            enhanced_response = enhance_response(base_response, query, result['intent'])
            
            if enhanced_response:
                # Tier 0 - AI can handle
                return {
                    'intent': result['intent'],
                    'confidence': result['confidence'],
                    'tier': 0,
                    'message': enhanced_response,
                    'automated': True
                }
            else:
                # Tier 1 - Basic human support needed
                suggested_response = get_gemini_response(
                    query,
                    "Please provide a response asking for more specific information about the medical query, maintaining a professional and helpful tone."
                ) or f"I understand you have a question about {result['intent'].replace('_', ' ')}. Could you please provide more specific information about your concern?"
                
                return {
                    'intent': result['intent'],
                    'confidence': result['confidence'],
                    'tier': 1,
                    'message': "I'll need to transfer you to a human agent for better assistance with your query.",
                    'suggested_response': suggested_response,
                    'automated': False
                }
                
        except Exception as e:
            print(f"Error processing query: {e}")
            return {'error': 'Internal server error'}, 500

api.add_resource(HealthQuery, '/predict')

if __name__ == '__main__':
    flask_app.run(debug=True, port=5000) 