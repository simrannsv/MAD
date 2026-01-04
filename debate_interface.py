"""
Interactive Multi-Agent Debate System
User enters custom prompt → Agents debate → See results in real-time
Works with main.py API server on port 8003
"""

import streamlit as st
import requests
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .agent-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .agent-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .agent-icon {
        font-size: 2rem;
    }
    
    .agent-response {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
        line-height: 1.8;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .verdict-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.4);
        animation: slideIn 0.8s ease;
    }
    
    .verdict-card h2 {
        margin: 0 0 1rem 0;
        font-size: 2rem;
    }
    
    .status-online {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-offline {
        color: #ef4444;
        font-weight: 600;
    }
    
    .round-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 1rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Agent configurations
AGENTS = {
    "Finance": {"icon": "💰", "color": "#10b981"},
    "Market": {"icon": "📊", "color": "#3b82f6"},
    "Innovator": {"icon": "💡", "color": "#f59e0b"},
    "Risk Manager": {"icon": "⚠️", "color": "#ef4444"},
    "Devils Advocate": {"icon": "😈", "color": "#8b5cf6"},
    "Operator": {"icon": "⚙️", "color": "#6366f1"},
}

API_BASE = "http://localhost:8003"

def check_server_status():
    """Check if the API server is online"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def display_agent_response(agent_name, response_text, color):
    """Display an agent's response with styling"""
    st.markdown(f"""
    <div class="agent-card" style="border-left-color: {color};">
        <div class="agent-name">
            <span class="agent-icon">{AGENTS[agent_name]['icon']}</span>
            {agent_name}
        </div>
        <div class="agent-response">
            {response_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

def call_agent(agent_endpoint, prompt):
    """Call a specific agent endpoint"""
    try:
        response = requests.post(
            f"{API_BASE}/{agent_endpoint}",
            json={"prompt": prompt},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()['output']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error calling agent: {str(e)}"

def run_full_debate(prompt):
    """Run full debate using the /debate endpoint"""
    try:
        response = requests.post(
            f"{API_BASE}/debate",
            json={"prompt": prompt},
            timeout=300
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error running debate: {str(e)}")
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ AI Debate Arena</h1>
        <p style="font-size: 1.2rem; margin-top: 0.5rem;">Enter your topic • Watch AI agents debate • Get intelligent verdict</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Check server status
        is_online, health_info = check_server_status()
        
        if is_online:
            st.markdown('<p class="status-online">✅ API Server: Online</p>', unsafe_allow_html=True)
            if health_info:
                st.info(f"🤖 Model: {health_info.get('model', 'Unknown')}\n\n🔌 Ollama: {health_info.get('ollama', 'Unknown')}")
        else:
            st.markdown('<p class="status-offline">❌ API Server: Offline</p>', unsafe_allow_html=True)
            st.error("Start server with:\n`python main.py`")
        
        st.divider()
        
        st.header("👥 Debate Agents")
        
        debate_mode = st.radio(
            "Select mode:",
            ["Full Debate (Fastest)", "Individual Agents (See Each)"],
            help="Full Debate runs all agents in parallel. Individual shows each agent one by one."
        )
        
        st.divider()
        
        st.header("📋 Agent List")
        for agent, config in AGENTS.items():
            st.markdown(f"{config['icon']} **{agent}**")
        st.markdown("⚖️ **Synthesizer** (Final Verdict)")
        
        st.divider()
        
        st.header("💡 Example Topics")
        st.info("""
        • Should we invest $50M in our competitor?
        • Launch product early or wait?
        • Remote-first or hybrid work?
        • Raise prices by 30%?
        • Pivot to B2C marketplace?
        • Adopt 4-day work week?
        """)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💭 Enter Your Debate Topic")
        
        # Custom prompt input
        user_prompt = st.text_area(
            "What should the agents debate?",
            placeholder="e.g., Should we invest $10M in AI automation for our customer service department?",
            height=150,
            help="Enter any business decision, strategy question, or topic you want multiple expert perspectives on."
        )
    
    with col2:
        st.header("🎯 Quick Actions")
        
        if st.button("🚀 Start Debate", use_container_width=True, disabled=not is_online):
            if user_prompt.strip():
                st.session_state['run_debate'] = True
                st.session_state['prompt'] = user_prompt
            else:
                st.error("Please enter a topic first!")
        
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state['run_debate'] = False
            if 'prompt' in st.session_state:
                del st.session_state['prompt']
            st.rerun()
    
    # Run debate if triggered
    if st.session_state.get('run_debate', False):
        prompt = st.session_state.get('prompt', '')
        
        st.markdown("---")
        st.header("🎭 Debate in Progress")
        
        progress_placeholder = st.empty()
        
        if debate_mode == "Full Debate (Fastest)":
            # Use the /debate endpoint
            progress_placeholder.info("⏳ Running full debate with all agents...")
            
            result = run_full_debate(prompt)
            
            if result:
                progress_placeholder.empty()
                
                # Display topic
                st.markdown(f"**📌 Topic:** {prompt}")
                
                # Display agent responses
                st.markdown('<div class="round-badge">🔄 Agent Perspectives</div>', unsafe_allow_html=True)
                
                for agent_data in result['agent_responses']:
                    agent_name = agent_data['agent']
                    response = agent_data['response']
                    color = AGENTS.get(agent_name, {}).get('color', '#666')
                    
                    display_agent_response(agent_name, response, color)
                    time.sleep(0.3)  # Small delay for visual effect
                
                # Display verdict
                st.markdown("""
                <div class="verdict-card">
                    <h2>⚖️ Final Verdict - Synthesizer</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="agent-response" style="margin-top: -1rem;">
                    {result['final_verdict']['response']}
                </div>
                """, unsafe_allow_html=True)
                
                # Download option
                st.markdown("---")
                
                # Generate transcript
                transcript = f"# AI Debate Arena - Debate Transcript\n\n"
                transcript += f"**Topic:** {prompt}\n\n"
                transcript += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                transcript += "---\n\n"
                transcript += "## Agent Perspectives\n\n"
                
                for agent_data in result['agent_responses']:
                    transcript += f"### {agent_data['icon']} {agent_data['agent']}\n\n"
                    transcript += f"{agent_data['response']}\n\n"
                
                transcript += "---\n\n"
                transcript += "## ⚖️ Final Verdict - Synthesizer\n\n"
                transcript += f"{result['final_verdict']['response']}\n"
                
                st.download_button(
                    label="📥 Download Debate Transcript",
                    data=transcript,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                st.balloons()
        
        else:
            # Individual agent mode
            st.markdown(f"**📌 Topic:** {prompt}")
            
            agent_endpoints = {
                "Finance": "finance",
                "Market": "market",
                "Innovator": "innovator",
                "Risk Manager": "risk-manager",
                "Devils Advocate": "devils-advocate",
                "Operator": "operator",
            }
            
            total_agents = len(agent_endpoints) + 1  # +1 for synthesizer
            progress_bar = st.progress(0)
            
            responses = []
            
            # Get responses from each agent
            for idx, (agent_name, endpoint) in enumerate(agent_endpoints.items()):
                progress_placeholder.info(f"⏳ {AGENTS[agent_name]['icon']} {agent_name} is thinking...")
                
                response = call_agent(endpoint, prompt)
                responses.append((agent_name, response))
                
                display_agent_response(agent_name, response, AGENTS[agent_name]['color'])
                
                progress_bar.progress((idx + 1) / total_agents)
                time.sleep(0.5)
            
            # Get synthesizer verdict
            progress_placeholder.info("⏳ ⚖️ Synthesizer is analyzing all perspectives...")
            
            # Prepare context for synthesizer
            context = f"Topic: {prompt}\n\n"
            context += "All perspectives:\n"
            for agent_name, response in responses:
                context += f"{agent_name}: {response[:150]}...\n"
            
            verdict = call_agent("synthesizer", context)
            
            st.markdown("""
            <div class="verdict-card">
                <h2>⚖️ Final Verdict - Synthesizer</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="agent-response" style="margin-top: -1rem;">
                {verdict}
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar.progress(1.0)
            progress_placeholder.success("✅ Debate completed!")
            
            st.balloons()

if __name__ == "__main__":
    main()
