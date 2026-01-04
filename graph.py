from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from engine import DebateEngine
from synthesizer import Synthesizer
import asyncio

class DebateState(TypedDict):
    """State structure for the debate graph"""
    topic: str
    round: int
    history: List[str]
    final_verdict: str

# Initialize engines
debate_engine = DebateEngine()
synthesizer = Synthesizer()

def debate_round(state: DebateState) -> DebateState:
    """Execute one round of debate with all agents"""
    try:
        topic = state["topic"]
        current_round = state["round"]
        history = state["history"]
        
        print(f"\n{'='*60}")
        print(f"Executing Round {current_round}")
        print(f"{'='*60}")
        
        # Get the running event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, use run_coroutine_threadsafe
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    debate_engine._run_round_async(topic, current_round, history)
                )
                round_history = future.result()
        except RuntimeError:
            # No event loop running, create one
            round_history = asyncio.run(
                debate_engine._run_round_async(topic, current_round, history)
            )
        
        # Update history with this round's responses
        updated_history = history + round_history
        
        # Increment round
        next_round = current_round + 1
        
        return {
            "topic": topic,
            "round": next_round,
            "history": updated_history,
            "final_verdict": state["final_verdict"]
        }
        
    except Exception as e:
        print(f"Error in debate_round: {str(e)}")
        import traceback
        traceback.print_exc()
        return state

def should_continue(state: DebateState) -> str:
    """Determine if we should continue to next round or end"""
    if state["round"] <= 3:
        return "continue"
    else:
        return "synthesize"

def synthesize_verdict(state: DebateState) -> DebateState:
    """Generate final verdict from all rounds"""
    try:
        print(f"\n{'='*60}")
        print("Synthesizing Final Verdict...")
        print(f"{'='*60}")
        
        verdict = synthesizer.generate_verdict(
            topic=state["topic"],
            history=state["history"]
        )
        
        return {
            "topic": state["topic"],
            "round": state["round"],
            "history": state["history"],
            "final_verdict": verdict
        }
        
    except Exception as e:
        print(f"Error in synthesize_verdict: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "topic": state["topic"],
            "round": state["round"],
            "history": state["history"],
            "final_verdict": f"Error generating verdict: {str(e)}"
        }

# Build the graph
workflow = StateGraph(DebateState)

# Add nodes
workflow.add_node("debate_round", debate_round)
workflow.add_node("synthesize", synthesize_verdict)

# Set entry point
workflow.set_entry_point("debate_round")

# Add conditional edges
workflow.add_conditional_edges(
    "debate_round",
    should_continue,
    {
        "continue": "debate_round",
        "synthesize": "synthesize"
    }
)

# Add edge from synthesize to end
workflow.add_edge("synthesize", END)

# Compile the graph
app_engine = workflow.compile()

print("LangGraph debate system initialized successfully!")
