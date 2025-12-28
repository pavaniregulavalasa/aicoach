import logging
from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach

logger = logging.getLogger(__name__)

retrieve_training_content = services.ai_coach.retrieve_training_content

class TrainingAgent:
    def __init__(self):
        logger.info("Initializing TrainingAgent")
        try:
            self.comprehensive_coach = ComprehensiveTrainingCoach()
            logger.info("TrainingAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TrainingAgent: {str(e)}")
            logger.exception("Full traceback:")
            raise
    def handle_request(self, level, knowledge_base):
        logger.info("="*80)
        logger.info("TRAINING AGENT: Handling request")
        logger.info(f"  Level: {level}")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        # Based on the level, generate appropriate training content
        if level == "beginner":
            logger.info("Routing to beginner content generation")
            return self.generate_beginner_content(knowledge_base)
        elif level == "intermediate":
            logger.info("Routing to intermediate content generation")
            return self.generate_intermediate_content(knowledge_base)
        elif level == "advanced":
            logger.info("Routing to advanced content generation")
            return self.generate_advanced_content(knowledge_base)
        elif level == "architecture":
            logger.info("Routing to architecture content generation")
            return self.generate_architecture_content(knowledge_base)
        else:
            logger.warning(f"Invalid level requested: {level}")
            return {"error": "Invalid level. Please choose 'beginner', 'intermediate', 'advanced', or 'architecture'."}

    def generate_beginner_content(self,knowledge_base):
        logger.info("="*80)
        logger.info("GENERATING BEGINNER CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        # Generate beginner-level training content
        try:
            logger.info("Step 1: Retrieving training content from FAISS")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "beginner"
                })
            logger.info(f"Retrieved content length: {len(content)} characters")
            
            logger.info("Step 2: Generating comprehensive lesson via LLM")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "beginner", content)
            logger.info(f"Generated lesson length: {len(lesson)} characters")
            
            logger.info("Beginner content generation completed successfully")
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating beginner content: {error_msg}")
            logger.exception("Full traceback:")
            
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.error("Connection-related error detected")
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_intermediate_content(self,knowledge_base):
        logger.info("="*80)
        logger.info("GENERATING INTERMEDIATE CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        try:
            logger.info("Step 1: Retrieving training content from FAISS")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "intermediate"
                })
            logger.info(f"Retrieved content length: {len(content)} characters")
            
            logger.info("Step 2: Generating comprehensive lesson via LLM")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "intermediate", content)
            logger.info(f"Generated lesson length: {len(lesson)} characters")
            
            logger.info("Intermediate content generation completed successfully")
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating intermediate content: {error_msg}")
            logger.exception("Full traceback:")
            
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.error("Connection-related error detected")
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_advanced_content(self,knowledge_base):
        logger.info("="*80)
        logger.info("GENERATING ADVANCED CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        try:
            logger.info("Step 1: Retrieving training content from FAISS")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "advanced"
                })
            logger.info(f"Retrieved content length: {len(content)} characters")
            
            logger.info("Step 2: Generating comprehensive lesson via LLM")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "advanced", content)
            logger.info(f"Generated lesson length: {len(lesson)} characters")
            
            logger.info("Advanced content generation completed successfully")
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating advanced content: {error_msg}")
            logger.exception("Full traceback:")
            
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.error("Connection-related error detected")
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_architecture_content(self, knowledge_base):
        logger.info("="*80)
        logger.info("GENERATING ARCHITECTURE CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        try:
            logger.info("Step 1: Retrieving training content from FAISS")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "architecture"
                })
            logger.info(f"Retrieved content length: {len(content)} characters")
            
            logger.info("Step 2: Generating comprehensive lesson via LLM")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "architecture", content)
            logger.info(f"Generated lesson length: {len(lesson)} characters")
            
            logger.info("Architecture content generation completed successfully")
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating architecture content: {error_msg}")
            logger.exception("Full traceback:")
            
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.error("Connection-related error detected")
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }
