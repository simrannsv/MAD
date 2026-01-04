import asyncio
from agentfactory import AgentFactory
from typing import TypedDict, List

class DebateState(TypedDict):
    topic: str
    round: int
    history: List[str]

class DebateEngine:
    def __init__(self):
        self.agent_factory = AgentFactory()
    
    async def get_agent_response_async(self, agent_name: str, topic: str, round_num: int, history: list):
        """Async wrapper for the synchronous agent response"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.agent_factory.get_agent_response,
            agent_name,
            topic,
            round_num,
            history
        )
    
    def run_round(self, topic: str, round_num: int, history: List[str]) -> List[str]:
        """Synchronous method to run one debate round - called by LangGraph"""
        # Create an event loop and run the async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._run_round_async(topic, round_num, history))
            return result
        finally:
            loop.close()
    
    async def _run_round_async(self, topic: str, round_num: int, history: List[str]) -> List[str]:
        """Internal async method to execute the round"""
        agent_names = self.agent_factory.get_all_agents()
        
        # Create parallel tasks for all agents
        tasks = [
            self.get_agent_response_async(
                agent_name=agent_name,
                topic=topic,
                round_num=round_num,
                history=history
            )
            for agent_name in agent_names
        ]
        
        # Wait for all agents to finish
        responses = await asyncio.gather(*tasks)
        
        # Create history entries for this round
        round_history = [
            f"Round {round_num} | {agent_names[i]}: {response}" 
            for i, response in enumerate(responses)
        ]
        
        return round_history
    
    async def debate_round(self, state: DebateState):
        """Async method for running debate rounds (original method)"""
        agent_names = self.agent_factory.get_all_agents()
        
        tasks = [
            self.get_agent_response_async(
                agent_name=agent_name,
                topic=state['topic'],
                round_num=state['round'],
                history=state['history']
            )
            for agent_name in agent_names
        ]
        
        responses = await asyncio.gather(*tasks)
        
        new_history = [
            f"Round {state['round']} | {agent_names[i]}: {response}" 
            for i, response in enumerate(responses)
        ]
        
        return {
            "history": state['history'] + new_history,
            "round": state['round'] + 1
        }