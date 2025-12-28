import logging
from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach

logger = logging.getLogger(__name__)

retrieve_training_content = services.ai_coach.retrieve_training_content
LLM = services.ai_coach.LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class MentorAgent:
    """Agent that provides mentor-like guidance for technical questions"""
    
    def __init__(self):
        logger.info("Initializing MentorAgent")
        # Try to initialize coach, but don't fail if indexes are missing
        try:
            self.comprehensive_coach = ComprehensiveTrainingCoach()
            logger.info("MentorAgent initialized successfully with ComprehensiveTrainingCoach")
        except FileNotFoundError as e:
            # Coach not available, but we can still provide guidance
            logger.warning(f"ComprehensiveTrainingCoach not available (FileNotFoundError): {str(e)}")
            logger.warning("MentorAgent will continue without coach, using LLM directly")
            self.comprehensive_coach = None
        except Exception as e:
            logger.error(f"Unexpected error initializing MentorAgent: {str(e)}")
            logger.exception("Full traceback:")
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
        logger.info("="*80)
        logger.info("MENTOR AGENT: Handling request")
        logger.info(f"  Query: {query[:100]}..." if len(query) > 100 else f"  Query: {query}")
        logger.info(f"  Context: {context}")
        logger.info("="*80)
        
        # Try to retrieve relevant content from knowledge bases
        knowledge_bases = ["mml", "alarm_handling"]
        relevant_content = []
        
        logger.info(f"Searching {len(knowledge_bases)} knowledge bases for relevant content")
        for kb in knowledge_bases:
            try:
                logger.debug(f"Retrieving content from knowledge base: {kb}")
                content = retrieve_training_content.invoke({
                    "knowledge_base": kb,
                    "level": "advanced",
                    "topic": query
                })
                if content and not content.startswith("❌"):
                    logger.info(f"Found relevant content in {kb}: {len(content)} characters")
                    relevant_content.append(f"=== {kb.upper()} KNOWLEDGE BASE ===\n{content}\n")
                else:
                    logger.debug(f"No relevant content found in {kb}")
            except Exception as e:
                logger.warning(f"Error retrieving content from {kb}: {str(e)}")
                continue
        
        logger.info(f"Retrieved content from {len(relevant_content)} knowledge base(s)")
        
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
        
        logger.info("Building prompt chain for mentor response")
        chain = prompt | LLM | StrOutputParser()
        
        knowledge_content = "\n\n".join(relevant_content) if relevant_content else "No specific knowledge base content found. Use your general telecom expertise."
        logger.info(f"Prepared knowledge content: {len(knowledge_content)} characters")
        
        prompt_vars = {
            "query": query,
            "context": context,
            "knowledge_content": knowledge_content
        }
        
        logger.info("="*80)
        logger.info("SENDING MENTOR PROMPT TO LLM")
        logger.info(f"  Query length: {len(query)} characters")
        logger.info(f"  Context: {context}")
        logger.info(f"  Knowledge content length: {len(knowledge_content)} characters")
        logger.info("="*80)
        
        try:
            logger.info("Invoking LLM chain for mentor response...")
            mentor_response = chain.invoke(prompt_vars)
            
            logger.info("="*80)
            logger.info("MENTOR RESPONSE RECEIVED")
            logger.info(f"  Response length: {len(mentor_response)} characters")
            logger.debug(f"  Response preview (first 200 chars): {mentor_response[:200]}...")
            logger.info("="*80)
            
            return {
                "mentor_response": mentor_response
            }
        except Exception as e:
            logger.error("="*80)
            logger.error("MENTOR LLM INVOCATION FAILED")
            logger.error(f"  Error: {str(e)}")
            logger.error(f"  Query: {query}")
            logger.error(f"  Context: {context}")
            logger.exception("Full traceback:")
            logger.error("="*80)
            raise

