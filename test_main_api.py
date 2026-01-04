"""
Test client for main.py API endpoints
Shows how to call individual agent endpoints
"""

import requests
import json

API_BASE = "http://localhost:8003"

def test_single_agent(agent_endpoint, prompt):
    """Test a single agent endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {agent_endpoint}")
    print(f"{'='*60}\n")
    
    response = requests.post(
        f"{API_BASE}/{agent_endpoint}",
        json={"prompt": prompt}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Agent: {result['agent']}")
        print(f"Role: {result['role']}")
        print(f"\nResponse:\n{result['output']}\n")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_full_debate(prompt):
    """Test the full debate endpoint"""
    print(f"\n{'='*60}")
    print(f"FULL DEBATE")
    print(f"{'='*60}\n")
    print(f"Topic: {prompt}\n")
    
    response = requests.post(
        f"{API_BASE}/debate",
        json={"prompt": prompt}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("AGENT RESPONSES:")
        print("-" * 60)
        for agent in result['agent_responses']:
            print(f"\n{agent['icon']} {agent['agent']}:")
            print(agent['response'][:300] + "..." if len(agent['response']) > 300 else agent['response'])
        
        print("\n\n" + "="*60)
        print("⚖️  FINAL VERDICT - SYNTHESIZER")
        print("="*60 + "\n")
        print(result['final_verdict']['response'])
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health = response.json()
            print("\n✅ Server Status:")
            print(f"   API: {health['status']}")
            print(f"   Ollama: {health['ollama']}")
            print(f"   Model: {health['model']}")
            return True
        else:
            print("\n❌ Server is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server at", API_BASE)
        print("   Make sure to run: python main.py")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Multi-Agent API Test Client")
    print("="*60)
    
    # Check server
    if not check_server():
        exit(1)
    
    # Example topic
    topic = "Should we invest $10M in AI automation for customer service?"
    
    print("\n\nChoose test mode:")
    print("1. Test single agents individually")
    print("2. Test full debate (all agents)")
    print("3. Custom prompt")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        agents = ["finance", "market", "innovator", "risk-manager", "devils-advocate", "operator", "synthesizer"]
        
        for agent in agents:
            test_single_agent(agent, topic)
            input("\nPress Enter for next agent...")
    
    elif choice == "2":
        test_full_debate(topic)
    
    elif choice == "3":
        custom_topic = input("\nEnter your topic: ").strip()
        if custom_topic:
            test_full_debate(custom_topic)
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60 + "\n")

    