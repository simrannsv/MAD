from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal, Annotated
import os
from pathlib import Path
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
import operator
from typing_extensions import TypedDict
import json
import asyncio

app = FastAPI(title="Multi-Agent Debate System with LangGraph", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track debate cancellation
debate_cancelled = False

# ============= Pydantic Models =============
class DebateRequest(BaseModel):
    topic: str
    rounds: Optional[int] = 3

class AgentResponse(BaseModel):
    agent: str
    round: int
    stance: str
    arguments: List[str]
    response: str

class DebateResponse(BaseModel):
    topic: str
    rounds: List[List[AgentResponse]]
    synthesis: str
    verdict: str

# ============= LangGraph State Definition =============
class DebateState(TypedDict):
    topic: str
    current_round: int
    max_rounds: int
    agent_responses: Annotated[List[dict], operator.add]
    all_rounds: List[List[dict]]
    synthesis: str
    verdict: str
    current_agent_index: int

# ============= Initialize Ollama LLM =============
llm = Ollama(
    model="llama3.2:3b",
    base_url="http://localhost:11434",
    temperature=0.8  # Increased for more diversity
)

# ============= Agent Definitions =============
AGENTS = [
    {
        "name": "Finance",
        "icon": "💰",
        "endpoint": "/finance",
        "role": "Financial Analyst",
        "perspective": "Analyze financial implications, ROI, costs, revenue impact, and profitability.",
        "system_prompt": """You are the Chief Financial Officer (CFO). Your ONLY concern is money and financial performance.
You analyze every decision through the lens of: profit margins, revenue growth, cost reduction, ROI, cash flow, and shareholder value.
You tend to be conservative and focus on proven financial strategies.
Be direct and opinionated. Use financial terminology."""
    },
    {
        "name": "Market",
        "icon": "📊",
        "endpoint": "/market",
        "role": "Market Analyst",
        "perspective": "Evaluate market trends, competition, customer behavior.",
        "system_prompt": """You are the Chief Marketing Officer (CMO). You obsess over customers, market positioning, and competitive advantage.
You analyze: customer sentiment, market share, brand perception, competitor moves, and market trends.
You prioritize customer satisfaction and market dominance over short-term profits.
Be strategic and customer-focused. Quote market data when possible."""
    },
    {
        "name": "Innovator",
        "icon": "💡",
        "endpoint": "/innovator",
        "role": "Innovation Lead",
        "perspective": "Focus on innovation opportunities and creative solutions.",
        "system_prompt": """You are the Chief Innovation Officer (CIO). You think about the future and disruptive possibilities.
You challenge the status quo and push for bold, innovative solutions. You care about: differentiation, technological edge, and long-term vision.
You're optimistic and forward-thinking, sometimes at odds with risk-averse colleagues.
Be visionary and enthusiastic about new ideas."""
    },
    {
        "name": "Risk Manager",
        "icon": "⚠️",
        "endpoint": "/risk-manager",
        "role": "Risk Assessment",
        "perspective": "Identify risks and mitigation strategies.",
        "system_prompt": """You are the Chief Risk Officer (CRO). Your job is to identify what could go wrong.
You analyze: regulatory risks, operational risks, reputational damage, legal issues, and worst-case scenarios.
You're naturally cautious and often push back on risky proposals. You demand contingency plans.
Be thorough in identifying potential problems and failures."""
    },
    {
        "name": "Devils Advocate",
        "icon": "😈",
        "endpoint": "/devils-advocate",
        "role": "Critical Analysis",
        "perspective": "Challenge assumptions and find flaws.",
        "system_prompt": """You are the Devil's Advocate. Your role is to challenge EVERYTHING and find holes in arguments.
Question assumptions, point out logical flaws, present counterarguments, and expose weaknesses.
You're contrarian by nature and enjoy poking holes in consensus. You ask "but what if..." constantly.
Be provocative and skeptical. Don't accept things at face value."""
    },
    {
        "name": "Operator",
        "icon": "⚙️",
        "endpoint": "/operator",
        "role": "Operations Manager",
        "perspective": "Assess operational feasibility and implementation.",
        "system_prompt": """You are the Chief Operations Officer (COO). You care about execution and practical implementation.
You analyze: resource requirements, timeline feasibility, team capacity, process efficiency, and operational complexity.
You're pragmatic and grounded. You ask "how will this actually work?" and "do we have the resources?"
Be practical and implementation-focused. Question unrealistic plans."""
    }
]

SYNTHESIZER = {
    "name": "Synthesizer",
    "icon": "🔮",
    "endpoint": "/synthesizer",
    "role": "Executive Summary",
    "system_prompt": """You are the Chief Executive Officer (CEO). You must synthesize all perspectives and make a final decision.
Balance financial, market, innovation, risk, and operational considerations.
Provide a clear executive summary and decisive recommendation.
Your verdict should be actionable: Approve, Reject, or Modify with specific conditions."""
}

# ============= Agent Functions =============
def create_agent_prompt(agent: dict, state: DebateState) -> str:
    """Create detailed prompt for agent with full context"""
    topic = state['topic']
    current_round = state['current_round']
    
    prompt = f"""{agent['system_prompt']}

DEBATE TOPIC: {topic}
CURRENT ROUND: {current_round} of {state['max_rounds']}

"""
    
    # Add context from previous rounds
    if current_round > 1 and state['all_rounds']:
        prompt += "\n=== PREVIOUS DISCUSSIONS ===\n"
        for round_idx, round_responses in enumerate(state['all_rounds'], 1):
            if round_responses:
                prompt += f"\n--- Round {round_idx} ---\n"
                for resp in round_responses:
                    prompt += f"{resp['agent']}: {resp['response']}\n\n"
    
    # Add current round context (what others have said so far)
    if state['agent_responses']:
        prompt += "\n=== CURRENT ROUND (so far) ===\n"
        for resp in state['agent_responses']:
            prompt += f"{resp['agent']}: {resp['response']}\n\n"
    
    # Round-specific instructions
    if current_round == 1:
        prompt += """\n=== YOUR TASK ===
This is Round 1. Give your initial analysis from YOUR unique perspective.
Start by clearly stating your stance: SUPPORT, OPPOSE, or NEUTRAL.
Then provide 2-3 specific points that support your position from your role's viewpoint.
Keep response to 3-4 sentences maximum."""
    elif current_round == 2:
        prompt += """\n=== YOUR TASK ===
This is Round 2. You've heard from others. Now respond to their arguments.
- Address at least one other agent's point (agree, disagree, or qualify)
- Strengthen your position with new evidence or reasoning
- Stay true to your role's perspective
Keep response to 3-4 sentences maximum."""
    else:
        prompt += """\n=== YOUR TASK ===
This is Round 3 - FINAL STATEMENTS. Make your closing argument.
- Reinforce your strongest points
- Acknowledge valid concerns from others if relevant
- Give your final recommendation from your role's perspective
Keep response to 3-4 sentences maximum."""
    
    return prompt

async def agent_node_streaming(state: DebateState, agent: dict, stream_callback=None):
    """Process agent with streaming callback"""
    global debate_cancelled
    
    if debate_cancelled:
        return {"agent_responses": []}
    
    prompt = create_agent_prompt(agent, state)
    
    try:
        response = llm.invoke(prompt)
        
        # Enhanced stance detection
        stance = "Neutral"
        response_lower = response.lower()
        first_200 = response_lower[:200]
        
        # Look for explicit stance declarations
        if any(word in first_200 for word in ["support", "approve", "favor", "yes", "agree", "positive"]):
            stance = "Support"
        elif any(word in first_200 for word in ["oppose", "against", "reject", "no", "disagree", "negative"]):
            stance = "Oppose"
        
        agent_response = {
            "agent": agent['name'],
            "round": state['current_round'],
            "stance": stance,
            "arguments": [],
            "response": response.strip()
        }
        
        # Stream this response
        if stream_callback:
            await stream_callback({
                "type": "agent_response",
                "data": agent_response
            })
        
        return {"agent_responses": [agent_response]}
    
    except Exception as e:
        print(f"Error in agent {agent['name']}: {str(e)}")
        return {"agent_responses": []}

def round_coordinator(state: DebateState) -> DebateState:
    """Coordinate round transitions"""
    if state['agent_responses']:
        new_all_rounds = state['all_rounds'].copy()
        new_all_rounds.append(state['agent_responses'].copy())
        
        if state['current_round'] < state['max_rounds']:
            return {
                "all_rounds": new_all_rounds,
                "agent_responses": [],
                "current_round": state['current_round'] + 1,
                "current_agent_index": 0
            }
        else:
            return {
                "all_rounds": new_all_rounds,
                "agent_responses": []
            }
    return {}

async def synthesizer_node_streaming(state: DebateState, stream_callback=None):
    """Synthesizer with streaming"""
    topic = state['topic']
    
    all_arguments = []
    for round_idx, round_responses in enumerate(state['all_rounds']):
        all_arguments.append(f"\n=== Round {round_idx + 1} ===")
        for resp in round_responses:
            all_arguments.append(f"{resp['agent']} ({resp['stance']}): {resp['response']}")
    
    context = "\n".join(all_arguments)
    
    prompt = f"""{SYNTHESIZER['system_prompt']}

DEBATE TOPIC: {topic}

FULL DEBATE TRANSCRIPT:
{context}

=== YOUR TASK ===
As CEO, provide:
1. Executive Summary (2-3 sentences synthesizing all viewpoints)
2. Key Trade-offs (what are the main tensions?)
3. Final Decision: APPROVE / REJECT / MODIFY (with conditions)
4. Rationale (why this decision?)

Keep total response to 5-6 sentences."""
    
    try:
        synthesis_response = llm.invoke(prompt)
        
        # Extract verdict (look for approve/reject/modify)
        verdict_text = synthesis_response.lower()
        if "approve" in verdict_text or "proceed" in verdict_text:
            verdict = "APPROVED"
        elif "reject" in verdict_text or "decline" in verdict_text:
            verdict = "REJECTED"
        elif "modify" in verdict_text or "conditional" in verdict_text:
            verdict = "CONDITIONAL APPROVAL"
        else:
            verdict = "UNDER REVIEW"
        
        result = {
            "synthesis": synthesis_response.strip(),
            "verdict": verdict
        }
        
        if stream_callback:
            await stream_callback({
                "type": "synthesis",
                "data": result
            })
        
        return result
    except Exception as e:
        print(f"Error in synthesizer: {str(e)}")
        return {
            "synthesis": "Synthesis unavailable",
            "verdict": "Unable to generate verdict"
        }

# ============= Streaming Debate Function =============
async def run_debate_streaming(topic: str, num_rounds: int = 3):
    """Run debate with streaming updates"""
    global debate_cancelled
    debate_cancelled = False
    
    state = {
        "topic": topic,
        "current_round": 1,
        "max_rounds": num_rounds,
        "agent_responses": [],
        "all_rounds": [],
        "synthesis": "",
        "verdict": "",
        "current_agent_index": 0
    }
    
    # Send start event
    yield f"data: {json.dumps({'type': 'start', 'topic': topic, 'rounds': num_rounds})}\n\n"
    
    # Run rounds
    for round_num in range(1, num_rounds + 1):
        if debate_cancelled:
            yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
            return
        
        state['current_round'] = round_num
        state['agent_responses'] = []
        
        # Send round start
        yield f"data: {json.dumps({'type': 'round_start', 'round': round_num})}\n\n"
        
        # Each agent speaks
        for agent in AGENTS:
            if debate_cancelled:
                yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
                return
            
            # Send agent start
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent['name'], 'round': round_num})}\n\n"
            
            result = await agent_node_streaming(state, agent)
            
            if result['agent_responses']:
                agent_resp = result['agent_responses'][0]
                state['agent_responses'].append(agent_resp)
                
                # Send agent response
                yield f"data: {json.dumps({'type': 'agent_response', 'data': agent_resp})}\n\n"
            
            # Small delay for better UX
            await asyncio.sleep(0.1)
        
        # Round complete - update state with all responses from this round
        new_state = round_coordinator(state)
        state.update(new_state)
        
        yield f"data: {json.dumps({'type': 'round_complete', 'round': round_num})}\n\n"
    
    # Synthesis
    if not debate_cancelled:
        yield f"data: {json.dumps({'type': 'synthesis_start'})}\n\n"
        
        synthesis_result = await synthesizer_node_streaming(state)
        state.update(synthesis_result)
        
        yield f"data: {json.dumps({'type': 'synthesis', 'data': synthesis_result})}\n\n"
    
    # Complete
    yield f"data: {json.dumps({'type': 'complete'})}\n\n"

# ============= API Endpoints =============
@app.get("/council")
async def serve_council_ui():
    """Serve the Strategic Council HTML interface"""
    html_path = Path("strategic_council.html")
    if html_path.exists():
        return FileResponse(html_path)
    else:
        raise HTTPException(status_code=404, detail="strategic_council.html not found")

@app.get("/api/agents")
async def get_agents():
    """Get all agents"""
    all_agents = AGENTS + [SYNTHESIZER]
    return {
        "title": "Multi-Agent Debate API",
        "version": "2.0",
        "agents": all_agents,
        "status": "online"
    }

@app.post("/api/debate/stream")
async def debate_stream(request: DebateRequest):
    """Stream debate in real-time"""
    return StreamingResponse(
        run_debate_streaming(request.topic, request.rounds or 3),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/debate/stop")
async def stop_debate():
    """Stop ongoing debate"""
    global debate_cancelled
    debate_cancelled = True
    return {"status": "stopped"}

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Debate System with Streaming",
        "backend": "Ollama + LangGraph",
        "status": "running",
        "endpoints": {
            "council_ui": "/council",
            "agents": "/api/agents",
            "debate_stream": "/api/debate/stream (POST)",
            "debate_stop": "/api/debate/stop (POST)",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "backend": "Ollama",
        "framework": "LangGraph",
        "model": "llama3.2:3b"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

    