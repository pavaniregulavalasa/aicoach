import logging
from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach

logger = logging.getLogger(__name__)

retrieve_training_content = services.ai_coach.retrieve_training_content
LLM = services.ai_coach.LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class AssessmentAgent:
    """Agent that assesses user's approach and provides feedback with scores"""
    
    def __init__(self):
        logger.info("Initializing AssessmentAgent")
        # Try to initialize coach, but don't fail if indexes are missing
        try:
            self.comprehensive_coach = ComprehensiveTrainingCoach()
            logger.info("AssessmentAgent initialized successfully with ComprehensiveTrainingCoach")
        except FileNotFoundError as e:
            # Coach not available, but we can still provide assessment
            logger.warning(f"ComprehensiveTrainingCoach not available (FileNotFoundError): {str(e)}")
            logger.warning("AssessmentAgent will continue without coach, using LLM directly")
            self.comprehensive_coach = None
        except Exception as e:
            logger.error(f"Unexpected error initializing AssessmentAgent: {str(e)}")
            logger.exception("Full traceback:")
            self.comprehensive_coach = None
    
    def handle_request(self, scenario: str):
        """
        Assess user's approach to a scenario and provide feedback
        
        Args:
            scenario: User's description of their approach to a scenario
        
        Returns:
            Dictionary with feedback and score
        """
        logger.info("="*80)
        logger.info("ASSESSMENT AGENT: Handling request")
        logger.info(f"  Scenario: {scenario[:100]}..." if len(scenario) > 100 else f"  Scenario: {scenario}")
        logger.info("="*80)
        
        # Retrieve relevant content for assessment context
        knowledge_bases = ["mml", "alarm_handling"]
        relevant_content = []
        
        logger.info(f"Searching {len(knowledge_bases)} knowledge bases for assessment context")
        for kb in knowledge_bases:
            try:
                logger.debug(f"Retrieving content from knowledge base: {kb}")
                content = retrieve_training_content.invoke({
                    "knowledge_base": kb,
                    "level": "advanced",
                    "topic": scenario
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
        
        # Generate assessment
        prompt = ChatPromptTemplate.from_template("""
You are an **Expert Telecom Training Assessor** evaluating a learner's approach to a technical scenario.

**USER'S APPROACH**: {scenario}

**RELEVANT KNOWLEDGE BASE CONTENT**:
{knowledge_content}

**YOUR TASK**: Provide comprehensive assessment with:
1. **Strengths** - What the learner did well
2. **Areas for Improvement** - Specific gaps or issues
3. **Technical Accuracy** - Correctness of approach, commands, procedures
4. **Best Practices Alignment** - How well it follows industry standards
5. **Risk Assessment** - Potential issues or risks in the approach
6. **Recommendations** - Specific actionable improvements

**SCORING CRITERIA** (0-100):
- Technical Accuracy: 30 points
- Best Practices: 25 points
- Completeness: 20 points
- Risk Awareness: 15 points
- Innovation/Problem-Solving: 10 points

**OUTPUT FORMAT** (JSON):
{{
    "feedback": "Detailed feedback text covering all assessment points",
    "score": <integer 0-100>,
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "technical_notes": "Specific technical observations"
}}

**RESPONSE** (JSON only, no markdown):
        """)
        
        logger.info("Building prompt chain for assessment")
        chain = prompt | LLM | StrOutputParser()
        
        knowledge_content = "\n\n".join(relevant_content) if relevant_content else "No specific knowledge base content found. Assess based on general telecom best practices."
        logger.info(f"Prepared knowledge content: {len(knowledge_content)} characters")
        
        prompt_vars = {
            "scenario": scenario,
            "knowledge_content": knowledge_content
        }
        
        logger.info("="*80)
        logger.info("SENDING ASSESSMENT PROMPT TO LLM")
        logger.info(f"  Scenario length: {len(scenario)} characters")
        logger.info(f"  Knowledge content length: {len(knowledge_content)} characters")
        logger.info("="*80)
        
        try:
            logger.info("Invoking LLM chain for assessment...")
            assessment_text = chain.invoke(prompt_vars)
            
            logger.info("="*80)
            logger.info("ASSESSMENT RESPONSE RECEIVED")
            logger.info(f"  Response length: {len(assessment_text)} characters")
            logger.debug(f"  Response preview (first 200 chars): {assessment_text[:200]}...")
            logger.info("="*80)
        except Exception as e:
            logger.error("="*80)
            logger.error("ASSESSMENT LLM INVOCATION FAILED")
            logger.error(f"  Error: {str(e)}")
            logger.error(f"  Scenario: {scenario}")
            logger.exception("Full traceback:")
            logger.error("="*80)
            raise
        
        # Try to parse JSON response, fallback to text if parsing fails
        logger.info("Parsing assessment response (expecting JSON format)")
        try:
            # Clean up the response - remove markdown code blocks if present
            cleaned = assessment_text.strip()
            logger.debug(f"Original response length: {len(cleaned)}")
            
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
                logger.debug("Removed ```json prefix")
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
                logger.debug("Removed ``` prefix")
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                logger.debug("Removed ``` suffix")
            cleaned = cleaned.strip()
            
            logger.debug(f"Cleaned response length: {len(cleaned)}")
            logger.debug(f"Attempting JSON parse...")
            assessment_data = json.loads(cleaned)
            logger.info("JSON parsing successful")
            logger.debug(f"Parsed keys: {list(assessment_data.keys())}")
            
            # Ensure required fields
            if "score" not in assessment_data:
                logger.warning("Score not found in parsed JSON, using default: 75")
                assessment_data["score"] = 75  # Default score
            if "feedback" not in assessment_data:
                logger.warning("Feedback not found in parsed JSON, using raw text")
                assessment_data["feedback"] = assessment_text
            
            logger.info(f"Assessment parsed successfully: score={assessment_data.get('score')}")
            return {
                "feedback": assessment_data.get("feedback", assessment_text),
                "score": assessment_data.get("score", 75),
                "strengths": assessment_data.get("strengths", []),
                "improvements": assessment_data.get("improvements", []),
                "technical_notes": assessment_data.get("technical_notes", "")
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"JSON parsing failed: {str(e)}")
            logger.warning("Falling back to text extraction")
            # Fallback: extract score from text or use default
            score = 75
            if "score" in assessment_text.lower():
                # Try to extract number
                import re
                score_match = re.search(r'score["\']?\s*:\s*(\d+)', assessment_text, re.IGNORECASE)
                if score_match:
                    score = int(score_match.group(1))
                    logger.info(f"Extracted score from text: {score}")
                else:
                    logger.warning("Could not extract score from text, using default: 75")
            else:
                logger.warning("No score found in text, using default: 75")
            
            logger.info("Returning fallback assessment response")
            return {
                "feedback": assessment_text,
                "score": score,
                "strengths": [],
                "improvements": [],
                "technical_notes": ""
            }

