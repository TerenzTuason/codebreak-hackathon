import requests
import json
from time import sleep

def test_query(query):
    url = "http://localhost:5000/predict"
    headers = {"Content-Type": "application/json"}
    data = {"query": query}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"\n📝 Query: {query}")
        print(f"🎯 Intent: {result['intent']}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print(f"📋 Tier: {result['tier']} ({'AI Support' if result['tier'] == 0 else 'Human Support' if result['tier'] == 1 else 'Specialist Support' if result['tier'] == 2 else 'Senior Medical Team' if result['tier'] == 3 else 'Critical/Legal Team'})")
        print(f"💬 Response: {result['message']}")
        if 'suggested_response' in result:
            print(f"💡 Suggested Response: {result['suggested_response']}")
        if 'required_data' in result:
            print(f"📋 Required Data: {', '.join(result['required_data'])}")
        if 'escalation_contact' in result and result['escalation_contact']:
            contact = result['escalation_contact']
            print(f"👤 Escalation Contact: {contact['name']} ({contact['email']}, {contact['phone']})")
        if 'priority' in result:
            print(f"⚡ Priority: {result['priority']}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error testing query: {query}")
        print(f"Error details: {str(e)}")
        return None

# Test different types of queries
test_cases = [
    # Test Tier 0 (should be handled by AI)
    "When is Dr. Miller available?",
    "What services does cardiology offer?",
    "Does HealthFirst cover vaccinations?",
    
    # Test Tier 1 (should be escalated to human)
    "I'm having severe chest pain and difficulty breathing",
    "My medication is causing unexpected side effects",
    
    # Test Tier 2 (requires specialist intervention)
    "Why was my insurance claim denied?",
    "Can I get a referral to a neurologist?",
    "My current medication isn't working. Can it be adjusted?",
    "I was double-booked with another patient. Can you fix it?",
    "What does my cholesterol result mean?",
    "Am I eligible for surgery under Medicare?",
    
    # Test Tier 3 (requires senior medical team)
    "I need help with a rare disease diagnosis",
    "I think my medical data was accessed without permission",
    "Are there clinical trials available for migraines?",
    
    # Test Tier 4 (critical/legal/VIP cases)
    "I need legal advice for a medical billing issue",
    "Can you arrange priority treatment for me?",
    "How do I arrange hospice care for a family member?",
    "Is it safe to take ibuprofen with my current medications?",
    "My cancer treatment was denied by insurance. What are my options?",
    
    # Test edge cases
    "What time does Dr. Unknown work?",
    "Does some-random-insurance cover my treatment?"
]

if __name__ == "__main__":
    print("\n🏥 Testing Healthcare Support AI API")
    print("=" * 50)
    
    for query in test_cases:
        test_query(query)
        print("-" * 50)
        sleep(1)  # Add small delay between requests 