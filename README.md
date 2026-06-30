# 🧠 MAD - Multi-Agent Debate System

MAD (Multi-Agent Debate System) is a locally deployed multi-agent AI application that simulates collaborative decision-making through structured debates between specialized AI agents. Instead of relying on a single LLM response, MAD enables multiple AI agents with distinct roles to analyze, debate, and refine their perspectives before producing a final, well-balanced verdict.

The project demonstrates how **multi-agent collaboration** can improve reasoning quality by combining domain-specific expertise with iterative discussion.

---

## 🚀 Overview

Real-world decisions require inputs from multiple perspectives rather than a single opinion. MAD recreates this process by assigning different responsibilities to specialized AI agents.

Each agent independently evaluates the user's query, participates in multiple rounds of debate, and refines its reasoning after considering arguments from other agents. Finally, a Synthesizer Agent combines all viewpoints into a structured and explainable final decision.

The system runs entirely **locally using Ollama**, ensuring privacy while eliminating dependence on external LLM APIs.

---

## ✨ Features

- 🤖 Multi-agent architecture with specialized AI agents
- 💬 Multi-round debate for iterative reasoning
- 📊 Role-based analysis from multiple business perspectives
- 🔄 Shared conversation state between agents
- 📝 Final synthesized verdict with explainable reasoning
- ⚡ Local LLM inference using Ollama
- 🌐 FastAPI backend for orchestration and API communication
- 🧩 Modular architecture for adding new agents and workflows

---

# 🏗️ System Architecture

```
                User Query
                     │
                     ▼
         ┌────────────────────┐
         │ Shared State Memory │
         └────────────────────┘
                     │
                     ▼
 ┌─────────┬──────────┬──────────┬──────────┬──────────┬─────────────┐
 │Finance  │ Market   │Innovation│Operations│ Risk     │ Devil's     │
 │ Agent   │ Analyst  │  Agent   │  Agent   │ Manager  │ Advocate    │
 └─────────┴──────────┴──────────┴──────────┴──────────┴─────────────┘
                     │
         Multi-Round Debate Process
                     │
                     ▼
          ┌─────────────────────┐
          │ Synthesizer Agent   │
          └─────────────────────┘
                     │
                     ▼
            Final Structured Verdict
```

---

# 🤖 Agents

### 💰 Finance Agent
Evaluates financial feasibility, ROI, investment requirements, and cost implications.

### 📈 Market Analyst
Analyzes market demand, competition, customer trends, and business opportunities.

### 💡 Innovator Agent
Evaluates novelty, creativity, and product differentiation.

### ⚙️ Operations Agent
Examines scalability, implementation complexity, and operational feasibility.

### ⚠️ Risk Manager
Identifies technical, financial, and business risks associated with the decision.

### 😈 Devil's Advocate
Challenges assumptions and presents opposing viewpoints to improve reasoning quality.

### 🧠 Synthesizer Agent
Collects all agent responses and produces the final balanced recommendation.

---

# 🔄 Workflow

1. User submits a business or strategic query.
2. The query is shared with all specialized agents.
3. Each agent generates an independent opinion.
4. Agents participate in multiple debate rounds.
5. Agents refine their responses after reviewing others' arguments.
6. The Synthesizer Agent combines all perspectives.
7. The system returns a structured final verdict.

---

# 🛠️ Tech Stack

### Language
- Python

### Backend
- FastAPI
- Uvicorn

### AI
- Ollama
- Llama 3.2

### Architecture
- Multi-Agent Systems
- REST APIs
- Shared State Management

---

# 📂 Project Structure

```
MAD/
│
├── agents/
│   ├── finance.py
│   ├── market.py
│   ├── innovation.py
│   ├── operations.py
│   ├── risk.py
│   ├── devil_advocate.py
│   └── synthesizer.py
│
├── backend/
│   ├── api.py
│   ├── debate.py
│   └── state.py
│
├── prompts/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# ▶️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/MAD.git
cd MAD
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start Ollama

```bash
ollama serve
```

Download the required model:

```bash
ollama pull llama3.2
```

---

# ▶️ Run the Application

```bash
uvicorn api:app --host 0.0.0.0 --port 8005
```

Open:

```
http://localhost:8005/docs
```

---

# 💬 Example Query

```
Should a startup launch an AI-powered financial assistant for students?
```

The system evaluates the idea from financial, operational, innovation, market, and risk perspectives before generating a comprehensive recommendation.

---

# 💡 Future Improvements

- Persistent agent memory
- Human approval workflow
- Market-aware external data integration
- Agent confidence scoring
- Long-term conversational memory
- Cloud deployment
- Interactive web dashboard

---

# 🎯 Applications

- Business Decision Support
- Startup Idea Validation
- Strategic Planning
- Product Evaluation
- Multi-Perspective Analysis
- AI Research

---

# 📖 Key Learnings

This project explores:
- Multi-Agent AI Systems
- Agent Orchestration
- Local LLM Deployment
- API Development
- Role-Based Prompt Engineering
- Collaborative AI Reasoning

---

# 👩‍💻 Author

**Simran Varthavani**

Exploring AI Agents, LLM Applications, Automation, and Intelligent Decision Systems.
