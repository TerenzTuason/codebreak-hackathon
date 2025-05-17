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

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": ["*"]}})  # Allow all origins in production
api = Api(app)

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
try:
    with open(os.path.join(os.path.dirname(__file__), 'datasets/healthcare_support_data.json'), 'r') as f:
        healthcare_data = json.load(f)
except Exception as e:
    print(f"Error loading healthcare data: {e}")
    healthcare_data = {"queries": [], "data_sources": {}}

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
            
            # Fill template with relevant data
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
        # Prepare prompt with context
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
            
            # Get appropriate response
            base_response = get_response_template(result['intent'], query)
            
            # If confidence is too low or no appropriate response, try Gemini
            if result['confidence'] < 0.4 or not base_response:
                gemini_response = get_gemini_response(query)
                if gemini_response:
                    return {
                        'intent': result['intent'],
                        'confidence': 0.7,  # Set reasonable confidence for Gemini responses
                        'tier': 0,
                        'message': gemini_response,
                        'automated': True
                    }
                else:
                    return {
                        'intent': result['intent'],
                        'confidence': result['confidence'],
                        'tier': 1,
                        'message': 'This query requires human assistance for a more accurate response.',
                        'suggested_response': 'I apologize, but I need more information to assist you properly. Could you please provide more details about your query?'
                    }
            
            # Enhance the base response with Gemini
            enhanced_response = enhance_response(base_response, query, result['intent'])
            
            # Handle Tier 0 response
            return {
                'intent': result['intent'],
                'confidence': result['confidence'],
                'tier': 0,
                'message': enhanced_response,
                'automated': True
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(HealthQuery, '/predict')

# For Vercel serverless deployment
app = app.wsgi_app

# Entry point for Vercel
def handler(event, context):
    return app

if __name__ == '__main__':
    app.run(debug=True, port=5000) 