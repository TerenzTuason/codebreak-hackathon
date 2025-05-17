from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from train import HealthcareSupportAI
import json

app = Flask(__name__)
api = Api(app)

# Initialize AI model
ai_model = HealthcareSupportAI()

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

def get_response_template(intent, query):
    """Get the appropriate response template and fill it with data"""
    for q in healthcare_data['queries']:
        if q['intent'] == intent:
            template = q['response_template']
            
            # Fill template with relevant data
            if intent == 'doctor_availability':
                for doc in healthcare_data['data_sources']['doctors']:
                    if doc['name'].lower() in query.lower():
                        return template.format(
                            doctor=doc['name'],
                            availability=', '.join(doc['availability']),
                            time=doc['time'],
                            room=doc['room']
                        )
            
            elif intent == 'department_services':
                for dept in healthcare_data['data_sources']['departments']:
                    if dept['name'].lower() in query.lower():
                        return template.format(
                            department=dept['name'],
                            services=', '.join(dept['services'])
                        )
            
            elif intent == 'insurance_coverage':
                for ins in healthcare_data['data_sources']['insurance_partners']:
                    if ins['name'].lower() in query.lower():
                        return template.format(
                            insurance_provider=ins['name'],
                            services_covered=', '.join(ins['services_covered']),
                            contact=ins['contact']
                        )
            
            elif intent == 'policy_inquiry':
                if 'cancel' in query.lower():
                    return healthcare_data['data_sources']['policies']['cancellation_policy']
                elif 'bill' in query.lower():
                    return healthcare_data['data_sources']['policies']['billing_policy']
                else:
                    return healthcare_data['data_sources']['policies']['data_privacy_policy']
                    
            return template
    return None

class HealthQuery(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            if not data or 'query' not in data:
                return {'error': 'No query provided'}, 400
                
            # Get intent prediction
            result = ai_model.predict(data['query'])
            
            # Get appropriate response
            response_message = get_response_template(result['intent'], data['query'])
            
            # If confidence is too low or no appropriate response, escalate to Tier 1
            if result['confidence'] < 0.7 or not response_message:
                return {
                    'intent': result['intent'],
                    'confidence': result['confidence'],
                    'tier': 1,
                    'message': 'This query requires human assistance for a more accurate response.',
                    'suggested_response': response_message if response_message else 'No automated response available.'
                }
            
            # Handle Tier 0 response
            return {
                'intent': result['intent'],
                'confidence': result['confidence'],
                'tier': 0,
                'message': response_message,
                'automated': True
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(HealthQuery, '/predict')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 