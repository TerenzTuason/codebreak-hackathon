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
        print(f"📋 Tier: {result['tier']} ({'AI Support' if result['tier'] == 0 else 'Human Support'})")
        print(f"💬 Response: {result['message']}")
        if 'suggested_response' in result:
            print(f"💡 Suggested Response: {result['suggested_response']}")
        
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