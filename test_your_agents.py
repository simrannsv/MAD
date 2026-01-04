"""
Test script for your 7-agent debate system
Make sure llm_server.py is running on port 8001 before running this!
"""

from agentfactory_your_agents import AgentFactory

def test_all_agents():
    """Test all 7 agents including the Synthesizer"""
    print("=" * 70)
    print("🎯 MULTI-AGENT DEBATE SYSTEM TEST")
    print("=" * 70)
    
    factory = AgentFactory()
    
    topic = "Should we invest $10M in developing an AI-powered product recommendation system?"
    
    print(f"\n💭 Debate Topic: {topic}\n")
    
    # Get debate agents (excludes Synthesizer)
    debate_agents = factory.get_debate_agents()
    print(f"👥 Debate Agents ({len(debate_agents)}): {', '.join(debate_agents)}")
    print(f"⚖️  Final Verdict by: {factory.get_synthesizer()}\n")
    
    history = []
    
    # Round 1: Initial positions
    print("\n" + "=" * 70)
    print("🔄 ROUND 1: Initial Analysis")
    print("=" * 70 + "\n")
    
    for agent_name in debate_agents:
        print(f"🗣️  {agent_name}:")
        print("-" * 70)
        
        response = factory.get_agent_response(
            agent_name=agent_name,
            topic=topic,
            round_num=1,
            history=history
        )
        
        print(response)
        history.append(f"[Round 1] {agent_name}: {response[:200]}...")
        print("\n")
    
    # Round 2: Responses and rebuttals
    print("\n" + "=" * 70)
    print("🔄 ROUND 2: Responses & Rebuttals")
    print("=" * 70 + "\n")
    
    for agent_name in debate_agents:
        print(f"🗣️  {agent_name}:")
        print("-" * 70)
        
        response = factory.get_agent_response(
            agent_name=agent_name,
            topic=topic,
            round_num=2,
            history=history
        )
        
        print(response)
        history.append(f"[Round 2] {agent_name}: {response[:200]}...")
        print("\n")
    
    # Final: Synthesizer gives verdict
    print("\n" + "=" * 70)
    print("⚖️  FINAL VERDICT - SYNTHESIZER")
    print("=" * 70 + "\n")
    
    synthesizer_response = factory.get_agent_response(
        agent_name="Synthesizer",
        topic=topic,
        round_num=3,
        history=history
    )
    
    print(synthesizer_response)
    
    print("\n" + "=" * 70)
    print("✅ DEBATE COMPLETED!")
    print("=" * 70 + "\n")

def test_quick():
    """Quick test with just 3 agents"""
    print("=" * 70)
    print("🚀 QUICK TEST - 3 Agents Only")
    print("=" * 70)
    
    factory = AgentFactory()
    
    topic = "Should we adopt a 4-day work week?"
    test_agents = ["Finance", "Risk Manager", "Synthesizer"]
    
    print(f"\n💭 Topic: {topic}")
    print(f"👥 Testing: {', '.join(test_agents)}\n")
    
    history = []
    
    for agent_name in test_agents:
        print(f"\n🗣️  {agent_name}:")
        print("-" * 70)
        
        response = factory.get_agent_response(
            agent_name=agent_name,
            topic=topic,
            round_num=1,
            history=history
        )
        
        print(response)
        history.append(f"{agent_name}: {response[:100]}...")
        print()
    
    print("\n" + "=" * 70)
    print("✅ Quick test completed!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    import sys
    
    print("\n⚠️  Make sure llm_server.py is running on port 8001!\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        test_quick()
    else:
        print("Running full debate test (this will take a few minutes)...")
        print("For a quick test, run: python test_your_agents.py quick\n")
        test_all_agents()
