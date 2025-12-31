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
        
        # Validate level
        valid_levels = ["beginner", "intermediate", "advanced", "architecture"]
        if level not in valid_levels:
            logger.warning(f"Invalid level requested: {level}")
            return {
                "error": "Invalid level",
                "message": f"Invalid level '{level}'. Please choose one of: {', '.join(valid_levels)}."
            }
        
        logger.info(f"Routing to {level} content generation")
        return self.generate_content(level, knowledge_base)

    def generate_content(self, level: str, knowledge_base: str):
        """
        Generate training content for a given level and knowledge base.
        Refactored to eliminate code duplication - single method handles all levels.
        
        Args:
            level: Training level ('beginner', 'intermediate', 'advanced', 'architecture')
            knowledge_base: Knowledge base to use ('mml' or 'alarm_handling')
        
        Returns:
            Dictionary with training_content or error information
        """
        logger.info("="*80)
        logger.info(f"GENERATING {level.upper()} CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info("="*80)
        
        try:
            # Step 1: Retrieve training content from FAISS
            logger.info("Step 1: Retrieving training content from FAISS")
            content = retrieve_training_content.invoke({
                "knowledge_base": knowledge_base,
                "level": level
            })
            logger.info(f"Retrieved content length: {len(content)} characters")
            
            # Step 2: Generate comprehensive lesson via LLM
            logger.info("Step 2: Generating comprehensive lesson via LLM")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, level, content)
            logger.info(f"Generated lesson length: {len(lesson)} characters")
            
            logger.info(f"{level.title()} content generation completed successfully")
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating {level} content: {error_msg}")
            logger.exception("Full traceback:")
            
            # Check for connection-related errors
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.error("Connection-related error detected")
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            
            # Generic error response
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }
