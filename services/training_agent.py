import logging
import time
from datetime import datetime
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
        overall_start = time.time()
        logger.info("="*80)
        logger.info("🚀 GENERATING BEGINNER CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"⏱️  [TIMING] Overall start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        # Generate beginner-level training content
        try:
            # Step 1: FAISS retrieval
            step1_start = time.time()
            logger.info("📚 [STEP 1] Retrieving training content from FAISS...")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "beginner"
                })
            step1_elapsed = time.time() - step1_start
            logger.info(f"✅ [STEP 1] Completed in {step1_elapsed:.2f} seconds")
            logger.info(f"📊 [STEP 1] Retrieved content length: {len(content)} characters")
            
            # Step 2: LLM generation
            step2_start = time.time()
            logger.info("🤖 [STEP 2] Generating comprehensive lesson via LLM...")
            logger.info("🤖 [STEP 2] This is the longest step - LLM generation can take 30-120 seconds...")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "beginner", content)
            step2_elapsed = time.time() - step2_start
            logger.info(f"✅ [STEP 2] Completed in {step2_elapsed:.2f} seconds ({step2_elapsed/60:.2f} minutes)")
            logger.info(f"📊 [STEP 2] Generated lesson length: {len(lesson)} characters")
            
            overall_elapsed = time.time() - overall_start
            logger.info("="*80)
            logger.info("✅ Beginner content generation completed successfully")
            logger.info(f"⏱️  [TIMING] Total time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.2f} minutes)")
            logger.info(f"⏱️  [TIMING] Breakdown - FAISS: {step1_elapsed:.2f}s, LLM: {step2_elapsed:.2f}s")
            logger.info("="*80)
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
        overall_start = time.time()
        logger.info("="*80)
        logger.info("🚀 GENERATING INTERMEDIATE CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"⏱️  [TIMING] Overall start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Step 1: FAISS retrieval
            step1_start = time.time()
            logger.info("📚 [STEP 1] Retrieving training content from FAISS...")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "intermediate"
                })
            step1_elapsed = time.time() - step1_start
            logger.info(f"✅ [STEP 1] Completed in {step1_elapsed:.2f} seconds")
            logger.info(f"📊 [STEP 1] Retrieved content length: {len(content)} characters")
            
            # Step 2: LLM generation
            step2_start = time.time()
            logger.info("🤖 [STEP 2] Generating comprehensive lesson via LLM...")
            logger.info("🤖 [STEP 2] This is the longest step - LLM generation can take 30-120 seconds...")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "intermediate", content)
            step2_elapsed = time.time() - step2_start
            logger.info(f"✅ [STEP 2] Completed in {step2_elapsed:.2f} seconds ({step2_elapsed/60:.2f} minutes)")
            logger.info(f"📊 [STEP 2] Generated lesson length: {len(lesson)} characters")
            
            overall_elapsed = time.time() - overall_start
            logger.info("="*80)
            logger.info("✅ Intermediate content generation completed successfully")
            logger.info(f"⏱️  [TIMING] Total time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.2f} minutes)")
            logger.info(f"⏱️  [TIMING] Breakdown - FAISS: {step1_elapsed:.2f}s, LLM: {step2_elapsed:.2f}s")
            logger.info("="*80)
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
        overall_start = time.time()
        logger.info("="*80)
        logger.info("🚀 GENERATING ADVANCED CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"⏱️  [TIMING] Overall start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Step 1: FAISS retrieval
            step1_start = time.time()
            logger.info("📚 [STEP 1] Retrieving training content from FAISS...")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "advanced"
                })
            step1_elapsed = time.time() - step1_start
            logger.info(f"✅ [STEP 1] Completed in {step1_elapsed:.2f} seconds")
            logger.info(f"📊 [STEP 1] Retrieved content length: {len(content)} characters")
            
            # Step 2: LLM generation
            step2_start = time.time()
            logger.info("🤖 [STEP 2] Generating comprehensive lesson via LLM...")
            logger.info("🤖 [STEP 2] This is the longest step - LLM generation can take 30-120 seconds...")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "advanced", content)
            step2_elapsed = time.time() - step2_start
            logger.info(f"✅ [STEP 2] Completed in {step2_elapsed:.2f} seconds ({step2_elapsed/60:.2f} minutes)")
            logger.info(f"📊 [STEP 2] Generated lesson length: {len(lesson)} characters")
            
            overall_elapsed = time.time() - overall_start
            logger.info("="*80)
            logger.info("✅ Advanced content generation completed successfully")
            logger.info(f"⏱️  [TIMING] Total time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.2f} minutes)")
            logger.info(f"⏱️  [TIMING] Breakdown - FAISS: {step1_elapsed:.2f}s, LLM: {step2_elapsed:.2f}s")
            logger.info("="*80)
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
        overall_start = time.time()
        logger.info("="*80)
        logger.info("🚀 GENERATING ARCHITECTURE CONTENT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"⏱️  [TIMING] Overall start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Step 1: FAISS retrieval
            step1_start = time.time()
            logger.info("📚 [STEP 1] Retrieving training content from FAISS...")
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "architecture"
                })
            step1_elapsed = time.time() - step1_start
            logger.info(f"✅ [STEP 1] Completed in {step1_elapsed:.2f} seconds")
            logger.info(f"📊 [STEP 1] Retrieved content length: {len(content)} characters")
            
            # Step 2: LLM generation
            step2_start = time.time()
            logger.info("🤖 [STEP 2] Generating comprehensive lesson via LLM...")
            logger.info("🤖 [STEP 2] This is the longest step - LLM generation can take 30-120 seconds...")
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "architecture", content)
            step2_elapsed = time.time() - step2_start
            logger.info(f"✅ [STEP 2] Completed in {step2_elapsed:.2f} seconds ({step2_elapsed/60:.2f} minutes)")
            logger.info(f"📊 [STEP 2] Generated lesson length: {len(lesson)} characters")
            
            overall_elapsed = time.time() - overall_start
            logger.info("="*80)
            logger.info("✅ Architecture content generation completed successfully")
            logger.info(f"⏱️  [TIMING] Total time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.2f} minutes)")
            logger.info(f"⏱️  [TIMING] Breakdown - FAISS: {step1_elapsed:.2f}s, LLM: {step2_elapsed:.2f}s")
            logger.info("="*80)
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
