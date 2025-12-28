from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach
retrieve_training_content = services.ai_coach.retrieve_training_content
class TrainingAgent:
    def __init__(self):
        self.comprehensive_coach = ComprehensiveTrainingCoach()
    def handle_request(self, level, knowledge_base):
        # Based on the level, generate appropriate training content
        if level == "beginner":
            return self.generate_beginner_content(knowledge_base)
        elif level == "intermediate":
            return self.generate_intermediate_content(knowledge_base)
        elif level == "advanced":
            return self.generate_advanced_content(knowledge_base)
        elif level == "architecture":
            return self.generate_architecture_content(knowledge_base)
        else:
            return {"error": "Invalid level. Please choose 'beginner', 'intermediate', 'advanced', or 'architecture'."}

    def generate_beginner_content(self,knowledge_base):
        # Generate beginner-level training content
        try:
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "beginner"
                })
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "beginner", content)
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_intermediate_content(self,knowledge_base):
        # Generate intermediate-level training content
        try:
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "intermediate"
                })
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "intermediate", content)
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_advanced_content(self,knowledge_base):
        # Generate advanced-level training content
        try:
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "advanced"
                })
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "advanced", content)
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }

    def generate_architecture_content(self, knowledge_base):
        # Generate architecture-level training content
        try:
            content = retrieve_training_content.invoke({
                    "knowledge_base": knowledge_base,
                    "level": "architecture"
                })
            lesson = self.comprehensive_coach.generate_comprehensive_lesson(knowledge_base, "architecture", content)
            return {
                "training_content": lesson
            }
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return {
                    "error": "LLM Connection Error",
                    "message": f"Unable to connect to the AI model service. Please check your network connection and Ericsson ELI gateway access. Error: {error_msg}"
                }
            return {
                "error": "Training Generation Error",
                "message": f"Failed to generate training content: {error_msg}"
            }
