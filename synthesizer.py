import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

class Synthesizer:
    """Synthesizes debate into final verdict using LangChain"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1000,
            api_key=api_key
        )
    
    def generate_verdict(self, topic: str, history: list) -> str:
        """Generate final verdict based on all debate rounds"""
        
        if not history:
            return "No verdict: Insufficient debate history to make a decision."
        
        # Compile the full debate transcript
        history_text = "\n\n".join(history)
        
        prompt = f"""You are an impartial judge reviewing a debate between 6 experts.

Topic: {topic}

Full Debate Transcript (3 Rounds):
{history_text}

Your task:
1. Summarize the key arguments from all 6 expert perspectives
2. Identify areas of consensus and points of contention
3. Weigh the strength of evidence and reasoning from each perspective
4. Provide a balanced conclusion with actionable recommendations

Format your response as:
**Summary:** [Brief overview of the debate]
**Key Arguments:**
- Economic perspective: [summary]
- Technical perspective: [summary]
- Risk perspective: [summary]
- Customer perspective: [summary]
- Sustainability perspective: [summary]
- Implementation perspective: [summary]

**Areas of Consensus:** [Where experts agree]
**Points of Contention:** [Where experts disagree]
**Final Recommendation:** [Clear, actionable guidance]
**Justification:** [Rationale for your recommendation]"""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an unbiased judge skilled at weighing complex arguments objectively from multiple expert perspectives."),
                HumanMessage(content=prompt)
            ])
            return response.content
            
        except Exception as e:
            return f"Error generating verdict: {str(e)}"