"""
Test script for updated AgentFactory with local LLM server
Make sure llm_server.py is running before executing this!
"""

from agentfactory_updated import AgentFactory

def test_single_agent():
    """Test a single agent response"""
    print("=" * 60)
    print("Testing Single Agent Response")
    print("=" * 60)
    
    factory = AgentFactory()
    
    topic = "Should companies invest heavily in AI automation?"
    
    response = factory.get_agent_response(
        agent_name="Economic Analyst",
        topic=topic,
        round_num=1,
        history=[]
    )
    
    print(f"\n📊 Economic Analyst's Response:\n")
    print(response)
    print("\n" + "=" * 60 + "\n")

def test_multiple_agents():
    """Test multiple agents in sequence"""
    print("=" * 60)
    print("Testing Multiple Agents")
    print("=" * 60)
    
    factory = AgentFactory()
    
    topic = "Remote work vs. office work: Which is better?"
    agents = factory.get_all_agents()
    
    print(f"\n🎯 Topic: {topic}\n")
    print(f"👥 Agents participating: {len(agents)}\n")
    
    history = []
    
    for i, agent_name in enumerate(agents[:3]):  # Test first 3 agents
        print(f"\n--- Agent {i+1}: {agent_name} ---\n")
        
        response = factory.get_agent_response(
            agent_name=agent_name,
            topic=topic,
            round_num=1,
            history=history
        )
        
        print(response)
        history.append(f"{agent_name}: {response[:100]}...")  # Add to history
        print("\n" + "-" * 60)
    
    print("\n" + "=" * 60 + "\n")

def test_multi_round_debate():
    """Test a simple multi-round debate"""
    print("=" * 60)
    print("Testing Multi-Round Debate")
    print("=" * 60)
    
    factory = AgentFactory()
    
    topic = "Universal Basic Income: Pros and Cons"
    test_agents = ["Economic Analyst", "Risk Manager", "Sustainability Expert"]
    
    print(f"\n🎯 Topic: {topic}")
    print(f"👥 Agents: {', '.join(test_agents)}")
    print(f"🔄 Rounds: 2\n")
    
    history = []
    
    for round_num in range(1, 3):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}")
        print(f"{'='*60}\n")
        
        for agent_name in test_agents:
            print(f"\n🗣️  {agent_name}:\n")
            
            response = factory.get_agent_response(
                agent_name=agent_name,
                topic=topic,
                round_num=round_num,
                history=history
            )
            
            print(response)
            history.append(f"[Round {round_num}] {agent_name}: {response[:150]}...")
            print("\n" + "-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ Multi-round debate completed!")
    print("=" * 60 + "\n")

def main():
    """Run all tests"""
    print("\n🚀 Starting AgentFactory Tests with Local LLM Server\n")
    print("⚠️  Make sure llm_server.py is running on http://localhost:8000\n")
    
    try:
        # Test 1: Single agent
        test_single_agent()
        
        # Test 2: Multiple agents
        test_multiple_agents()
        
        # Test 3: Multi-round debate
        test_multi_round_debate()
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 Your AgentFactory is working with the local LLM server!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure llm_server.py is running: python llm_server.py")
        print("2. Check if Ollama is installed and has a model: ollama list")
        print("3. Verify your .env file has correct backend settings")
        print("4. Try: curl http://localhost:8000/health")

if __name__ == "__main__":
    main()
