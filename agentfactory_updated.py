import os
from dotenv import load_dotenv 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

class AgentFactory:
    """Factory for creating debate agents with different perspectives using LangChain"""
    
    def __init__(self):
        # UPDATED: Use local FastAPI LLM server instead of OpenAI
        # The server must be running at http://localhost:8000
        
        # LangChain's ChatOpenAI can work with any OpenAI-compatible API!
        # Just change the base_url and use a dummy API key
        self.llm = ChatOpenAI(
            model="default",  # Changed from "gpt-4o"
            temperature=0.7,
            max_tokens=500,
            api_key="dummy-key",  # Not used by our server, but LangChain requires it
            base_url="http://localhost:8002/v1"  # Point to our local server
        )
        
        # Define 6 different expert perspectives
        self.agents = {
            "Economic Analyst": {
                "role": "Economic and financial expert focusing on ROI, costs, and market trends",
                "perspective": "Analyze from a financial and economic perspective"
            },
            "Tech Innovator": {
                "role": "Technology expert focusing on innovation, scalability, and technical feasibility",
                "perspective": "Evaluate from a technological advancement perspective"
            },
            "Risk Manager": {
                "role": "Risk assessment expert focusing on potential downsides and mitigation",
                "perspective": "Identify risks, challenges, and potential failure points"
            },
            "Customer Advocate": {
                "role": "Customer experience expert focusing on user needs and satisfaction",
                "perspective": "Consider the impact on end-users and customers"
            },
            "Sustainability Expert": {
                "role": "Long-term sustainability expert focusing on ethical and environmental impact",
                "perspective": "Evaluate long-term sustainability and ethical implications"
            },
            "Implementation Strategist": {
                "role": "Practical implementation expert focusing on execution and operations",
                "perspective": "Focus on practical implementation and operational feasibility"
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
        
        # Create the prompt
        prompt = f"""You are {agent_name}, a {agent_info['role']}.

Debate Topic: {topic}

Round: {round_num} of 3

Your perspective: {agent_info['perspective']}
{context}

Provide your analysis and argument (2-3 paragraphs, be concise and specific). Consider what others have said and build upon or challenge their points."""

        try:
            # Call LangChain ChatOpenAI (now pointing to our local server)
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
