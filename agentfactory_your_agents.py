import os
from dotenv import load_dotenv 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

class AgentFactory:
    """Factory for creating debate agents with different perspectives using LangChain"""
    
    def __init__(self):
        # Connect to local LLM server (make sure it's running on port 8001)
        self.llm = ChatOpenAI(
            model="default",
            temperature=0.7,
            max_tokens=500,
            api_key="dummy-key",
            base_url="http://localhost:8002/v1",
            default_headers={"Content-Type": "application/json"}
        )
        
        # Define your 7 debate agents
        self.agents = {
            "Finance": {
                "role": "Financial expert analyzing costs, ROI, budget implications, and financial viability",
                "perspective": "Evaluate all financial aspects including costs, revenue potential, and financial risks"
            },
            "Market": {
                "role": "Market analyst focusing on market trends, competition, demand, and positioning",
                "perspective": "Analyze market opportunities, competitive landscape, and customer demand"
            },
            "Innovator": {
                "role": "Innovation expert focusing on creativity, technological advancement, and future potential",
                "perspective": "Explore innovative approaches, emerging technologies, and creative solutions"
            },
            "Risk Manager": {
                "role": "Risk assessment expert identifying potential problems, threats, and mitigation strategies",
                "perspective": "Identify all possible risks, failure points, and propose risk mitigation strategies"
            },
            "Devils Advocate": {
                "role": "Critical thinker who challenges assumptions and finds flaws in every argument",
                "perspective": "Question everything, challenge all assumptions, and point out weaknesses and contradictions"
            },
            "Operator": {
                "role": "Operations expert focusing on practical implementation, execution, and day-to-day feasibility",
                "perspective": "Focus on practical execution, operational challenges, and real-world implementation"
            },
            "Synthesizer": {
                "role": "Strategic synthesizer who analyzes all perspectives and provides final verdict",
                "perspective": "Synthesize all viewpoints, weigh pros and cons, and provide a balanced final recommendation"
            }
        }
    
    def get_agent_response(self, agent_name: str, topic: str, round_num: int, history: list) -> str:
        """Get response from a specific agent using LangChain"""
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent_info = self.agents[agent_name]
        
        # Build context from previous rounds
        context = ""
        if history:
            context = "\n\nPrevious discussion:\n" + "\n".join(history[-10:])  # Last 10 messages
        
        # Special prompt for Synthesizer (final verdict agent)
        if agent_name == "Synthesizer":
            prompt = f"""You are the Synthesizer, the final decision maker in this debate.

Debate Topic: {topic}

You have heard from all other agents:
{context}

Your task:
1. Summarize the key points from each perspective
2. Weigh the pros and cons
3. Identify the strongest arguments
4. Address the main concerns raised
5. Provide a clear, decisive recommendation

Give your final verdict in 3-4 paragraphs."""
        else:
            # Regular agent prompt
            prompt = f"""You are {agent_name}, a {agent_info['role']}.

Debate Topic: {topic}

Round: {round_num} of 3

Your perspective: {agent_info['perspective']}
{context}

Provide your analysis and argument (2-3 paragraphs, be concise and specific). Consider what others have said and build upon or challenge their points."""

        try:
            # Call LangChain ChatOpenAI (pointing to local server)
            response = self.llm.invoke([
                SystemMessage(content=f"You are {agent_name}, a {agent_info['role']}."),
                HumanMessage(content=prompt)
            ])
            
            return response.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def get_all_agents(self) -> list:
        """Return list of all agent names"""
        return list(self.agents.keys())
    
    def get_debate_agents(self) -> list:
        """Return list of debate agents (excluding Synthesizer)"""
        return [agent for agent in self.agents.keys() if agent != "Synthesizer"]
    
    def get_synthesizer(self) -> str:
        """Return the Synthesizer agent name"""
        return "Synthesizer"
