from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach

retrieve_training_content = services.ai_coach.retrieve_training_content
LLM = services.ai_coach.LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class MentorAgent:
    """Agent that provides mentor-like guidance for technical questions"""
    
    def __init__(self):
        # Try to initialize coach, but don't fail if indexes are missing
        try:
            self.comprehensive_coach = ComprehensiveTrainingCoach()
        except FileNotFoundError:
            # Coach not available, but we can still provide guidance
            self.comprehensive_coach = None
    
    def handle_request(self, query: str, context: str = "training"):
        """
        Provide mentor guidance for a technical question
        
        Args:
            query: User's technical question
            context: Context for the query (e.g., "training", "mml", "alarm_handling")
        
        Returns:
            Dictionary with mentor_response
        """
        # Try to retrieve relevant content from knowledge bases
        knowledge_bases = ["mml", "alarm_handling"]
        relevant_content = []
        
        for kb in knowledge_bases:
            try:
                content = retrieve_training_content.invoke({
                    "knowledge_base": kb,
                    "level": "advanced",
                    "topic": query
                })
                if content and not content.startswith("❌"):
                    relevant_content.append(f"=== {kb.upper()} KNOWLEDGE BASE ===\n{content}\n")
            except Exception:
                continue
        
        # Generate mentor response
        prompt = ChatPromptTemplate.from_template("""
You are a **Senior Telecom Engineer and Mentor** with decades of experience in Ericsson systems.

**USER'S QUESTION**: {query}

**CONTEXT**: {context}

**RELEVANT KNOWLEDGE BASE CONTENT**:
{knowledge_content}

**YOUR ROLE**: Provide expert, production-grade guidance as a senior mentor would:
1. **Direct Answer** - Clear, concise answer to the question
2. **Best Practices** - Industry-standard approaches and patterns
3. **Common Pitfalls** - What to watch out for
4. **Real-World Example** - Practical scenario or use case
5. **Next Steps** - Recommended actions or learning path
6. **Additional Resources** - Where to find more information

**STYLE**: 
- Professional but approachable
- Use examples from the knowledge base when available
- Be specific and actionable
- Reference exact commands, procedures, or architecture when relevant

**RESPONSE**:
        """)
        
        chain = prompt | LLM | StrOutputParser()
        
        knowledge_content = "\n\n".join(relevant_content) if relevant_content else "No specific knowledge base content found. Use your general telecom expertise."
        
        mentor_response = chain.invoke({
            "query": query,
            "context": context,
            "knowledge_content": knowledge_content
        })
        
        return {
            "mentor_response": mentor_response
        }

