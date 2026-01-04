"""
Multi-Agent Debate System - Individual Agent API Endpoints
Updated to use all 7 agents with Ollama chat API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional

app = FastAPI(
    title="Multi-Agent Debate API",
    description="Individual endpoints for each debate agent",
    version="2.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"  # Your downloaded model

class AgentRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

class AgentResponse(BaseModel):
    agent: str
    role: str
    output: str

async def call_ollama(system_role: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 500):
    """Call Ollama using chat API (better than generate)"""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload, timeout=120.0)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

# ============= AGENT ENDPOINTS =============

@app.post("/finance", response_model=AgentResponse)
async def finance_agent(request: AgentRequest):
    """💰 Finance Agent - Financial analysis and ROI assessment"""
    role = "You are a Finance expert analyzing costs, ROI, budget implications, and financial viability. Provide detailed financial analysis with specific numbers and projections when possible."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Finance",
        role="Financial Expert",
        output=output
    )

@app.post("/market", response_model=AgentResponse)
async def market_agent(request: AgentRequest):
    """📊 Market Agent - Market analysis and competitive landscape"""
    role = "You are a Market analyst focusing on market trends, competition, demand, and positioning. Analyze market opportunities and competitive dynamics."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Market",
        role="Market Analyst",
        output=output
    )

@app.post("/innovator", response_model=AgentResponse)
async def innovator_agent(request: AgentRequest):
    """💡 Innovator Agent - Innovation and technology advancement"""
    role = "You are an Innovation expert focusing on creativity, technological advancement, and future potential. Explore innovative approaches and emerging technologies."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Innovator",
        role="Innovation Expert",
        output=output
    )

@app.post("/risk-manager", response_model=AgentResponse)
async def risk_manager_agent(request: AgentRequest):
    """⚠️ Risk Manager Agent - Risk assessment and mitigation"""
    role = "You are a Risk Manager identifying potential problems, threats, and mitigation strategies. Focus on what could go wrong and how to prevent it."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Risk Manager",
        role="Risk Assessment Expert",
        output=output
    )

@app.post("/devils-advocate", response_model=AgentResponse)
async def devils_advocate_agent(request: AgentRequest):
    """😈 Devils Advocate - Critical thinking and challenging assumptions"""
    role = "You are a Devils Advocate who challenges assumptions and finds flaws in every argument. Question everything and point out weaknesses and contradictions."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Devils Advocate",
        role="Critical Thinker",
        output=output
    )

@app.post("/operator", response_model=AgentResponse)
async def operator_agent(request: AgentRequest):
    """⚙️ Operator Agent - Operations and practical implementation"""
    role = "You are an Operations expert focusing on practical implementation, execution, and day-to-day feasibility. Focus on how things actually get done."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Operator",
        role="Operations Expert",
        output=output
    )

@app.post("/synthesizer", response_model=AgentResponse)
async def synthesizer_agent(request: AgentRequest):
    """⚖️ Synthesizer Agent - Final verdict and strategic synthesis"""
    role = "You are the Synthesizer who analyzes all perspectives and provides a balanced final verdict. Weigh pros and cons from multiple viewpoints and give a clear recommendation."
    output = await call_ollama(role, request.prompt, request.temperature, request.max_tokens)
    return AgentResponse(
        agent="Synthesizer",
        role="Strategic Synthesizer",
        output=output
    )

# ============= UTILITY ENDPOINTS =============

@app.post("/debate")
async def full_debate(request: AgentRequest):
    """
    🎯 Run a full debate with all agents
    Each agent provides their perspective on the prompt
    """
    agents = [
        ("finance", "Finance", "💰"),
        ("market", "Market", "📊"),
        ("innovator", "Innovator", "💡"),
        ("risk-manager", "Risk Manager", "⚠️"),
        ("devils-advocate", "Devils Advocate", "😈"),
        ("operator", "Operator", "⚙️"),
    ]
    
    responses = []
    history = []
    
    # Round 1: Each agent gives their perspective
    for endpoint, name, icon in agents:
        output = await call_ollama(
            f"You are a {name}. Consider the following: {' '.join(history[-3:])}",
            request.prompt,
            request.temperature,
            request.max_tokens
        )
        responses.append({
            "agent": name,
            "icon": icon,
            "response": output
        })
        history.append(f"{name}: {output[:100]}...")
    
    # Synthesizer gives final verdict
    synthesizer_prompt = f"""
    Topic: {request.prompt}
    
    Perspectives from all agents:
    {chr(10).join(history)}
    
    Provide a balanced final verdict with clear recommendation.
    """
    
    verdict = await call_ollama(
        "You are the Synthesizer providing final strategic verdict",
        synthesizer_prompt,
        request.temperature,
        request.max_tokens
    )
    
    return {
        "topic": request.prompt,
        "agent_responses": responses,
        "final_verdict": {
            "agent": "Synthesizer",
            "icon": "⚖️",
            "response": verdict
        }
    }

@app.get("/")
async def root():
    """API information"""
    return {
        "title": "Multi-Agent Debate API",
        "version": "2.0",
        "agents": [
            {"name": "Finance", "endpoint": "/finance", "icon": "💰"},
            {"name": "Market", "endpoint": "/market", "icon": "📊"},
            {"name": "Innovator", "endpoint": "/innovator", "icon": "💡"},
            {"name": "Risk Manager", "endpoint": "/risk-manager", "icon": "⚠️"},
            {"name": "Devils Advocate", "endpoint": "/devils-advocate", "icon": "😈"},
            {"name": "Operator", "endpoint": "/operator", "icon": "⚙️"},
            {"name": "Synthesizer", "endpoint": "/synthesizer", "icon": "⚖️"}
        ],
        "special_endpoints": [
            {"name": "Full Debate", "endpoint": "/debate", "description": "Run complete debate with all agents"}
        ],
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
async def health():
    """Health check"""
    # Try to ping Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            ollama_status = "online" if response.status_code == 200 else "offline"
    except:
        ollama_status = "offline"
    
    return {
        "status": "healthy",
        "ollama": ollama_status,
        "model": MODEL_NAME
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Multi-Agent Debate API Server")
    print("="*60)
    print(f"\n📍 Server: http://localhost:8003")
    print(f"📚 Docs: http://localhost:8003/docs")
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"\n⚠️  Make sure Ollama is running: ollama list")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)

    