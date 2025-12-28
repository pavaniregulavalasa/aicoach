from services.training_agent import TrainingAgent
from services.mentor_agent import MentorAgent
from services.assessment_agent import AssessmentAgent

class AgentOrchestrator:
    """Routes requests to appropriate agents"""
    
    def __init__(self):
        self.training_agent = TrainingAgent()
        self.mentor_agent = MentorAgent()
        self.assessment_agent = AssessmentAgent()
    
    def route_to_training_agent(self, level: str, knowledge_base: str = "mml", topic: str = ""):
        """
        Route training request to training agent
        
        Args:
            level: Training level ('beginner', 'intermediate', 'advanced', 'architecture')
            knowledge_base: Knowledge base to use ('mml' or 'alarm_handling')
            topic: Optional specific topic for doubt clearing (currently not used but kept for API compatibility)
        
        Returns:
            Response from training agent
        """
        return self.training_agent.handle_request(level, knowledge_base)
    
    def route_to_mentor_agent(self, query: str, context: str = "training"):
        """
        Route mentor request to mentor agent
        
        Args:
            query: User's technical question
            context: Context for the query
        
        Returns:
            Response from mentor agent
        """
        return self.mentor_agent.handle_request(query, context)
    
    def route_to_assessment_agent(self, scenario: str):
        """
        Route assessment request to assessment agent
        
        Args:
            scenario: User's approach description
        
        Returns:
            Response from assessment agent
        """
        return self.assessment_agent.handle_request(scenario)

