import logging
from services.training_agent import TrainingAgent
from services.mentor_agent import MentorAgent
from services.assessment_agent import AssessmentAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Routes requests to appropriate agents"""
    
    def __init__(self):
        logger.info("Initializing AgentOrchestrator")
        logger.debug("Creating agent instances...")
        self.training_agent = TrainingAgent()
        logger.debug("TrainingAgent created")
        self.mentor_agent = MentorAgent()
        logger.debug("MentorAgent created")
        self.assessment_agent = AssessmentAgent()
        logger.debug("AssessmentAgent created")
        logger.info("AgentOrchestrator initialization complete")
    
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
        logger.info(f"Orchestrator: Routing to TrainingAgent")
        logger.debug(f"  Parameters: level={level}, knowledge_base={knowledge_base}, topic={topic}")
        response = self.training_agent.handle_request(level, knowledge_base)
        logger.debug(f"TrainingAgent response received, keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        return response
    
    def route_to_mentor_agent(self, query: str, context: str = "training"):
        """
        Route mentor request to mentor agent
        
        Args:
            query: User's technical question
            context: Context for the query
        
        Returns:
            Response from mentor agent
        """
        logger.info(f"Orchestrator: Routing to MentorAgent")
        logger.debug(f"  Query length: {len(query)}, context: {context}")
        response = self.mentor_agent.handle_request(query, context)
        logger.debug(f"MentorAgent response received, keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        return response
    
    def route_to_assessment_agent(self, scenario: str):
        """
        Route assessment request to assessment agent
        
        Args:
            scenario: User's approach description
        
        Returns:
            Response from assessment agent
        """
        logger.info(f"Orchestrator: Routing to AssessmentAgent")
        logger.debug(f"  Scenario length: {len(scenario)}")
        response = self.assessment_agent.handle_request(scenario)
        logger.debug(f"AssessmentAgent response received, keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        return response

