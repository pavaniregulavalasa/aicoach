import logging
import sys
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from services.agent_orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/api_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
import os
os.makedirs('logs', exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="AI Telecom Training Coach API",
    description="Backend API for AI-powered telecom training platform",
    version="1.0.0"
)

logger.info("="*80)
logger.info("FastAPI application initialized")
logger.info("="*80)

# Agent Orchestrator instance (lazy initialization to avoid startup errors)
agent_orchestrator = None

def get_agent_orchestrator():
    """Lazy initialization of agent orchestrator"""
    global agent_orchestrator
    if agent_orchestrator is None:
        logger.info("Initializing AgentOrchestrator (lazy initialization)")
        agent_orchestrator = AgentOrchestrator()
        logger.info("AgentOrchestrator initialized successfully")
    else:
        logger.debug("Using existing AgentOrchestrator instance")
    return agent_orchestrator

# Request models
class TrainingRequest(BaseModel):
    level: str  # Training level: 'beginner', 'intermediate', 'advanced', or 'architecture'
    knowledge_base: str = "mml"  # Knowledge base: 'mml' or 'alarm_handling'
    topic: str = ""  # Optional specific topic for doubt clearing

class MentorRequest(BaseModel):
    query: str  # User's technical question
    context: str = "training"  # Context for the query

class AssessmentRequest(BaseModel):
    scenario: str  # User's approach to the scenario

# Endpoint to request training from the training agent
@app.post("/training")
async def training(request: TrainingRequest):
    """Generate training content based on level and knowledge base"""
    logger.info("="*80)
    logger.info(f"TRAINING REQUEST RECEIVED")
    logger.info(f"  Level: {request.level}")
    logger.info(f"  Knowledge Base: {request.knowledge_base}")
    logger.info(f"  Topic: {request.topic}")
    logger.info("="*80)
    
    try:
        logger.debug("Getting agent orchestrator")
        orchestrator = get_agent_orchestrator()
        
        logger.info(f"Routing to training agent: level={request.level}, kb={request.knowledge_base}, topic={request.topic}")
        response = orchestrator.route_to_training_agent(
            request.level, 
            request.knowledge_base, 
            request.topic
        )
        
        if "error" in response:
            logger.error(f"Training agent returned error: {response.get('error')}")
            logger.error(f"Error message: {response.get('message', 'No message')}")
        else:
            logger.info("Training content generated successfully")
            logger.debug(f"Response keys: {list(response.keys())}")
            if "training_content" in response:
                content_length = len(response["training_content"])
                logger.info(f"Training content length: {content_length} characters")
        
        return response
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError in training endpoint: {str(e)}")
        logger.exception("Full traceback:")
        return {
            "error": str(e),
            "message": "Please run services/rag.py first to create FAISS indexes"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception in training endpoint: {error_msg}")
        logger.exception("Full traceback:")
        
        # Provide more specific error messages for connection issues
        if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            logger.error("Connection-related error detected")
            return {
                "error": "LLM Connection Error",
                "message": f"Unable to connect to the AI model service (Ericsson ELI gateway). Please check:\n1. Network connectivity\n2. VPN access (if required)\n3. Ericsson ELI gateway availability\n\nTechnical error: {error_msg}"
            }
        return {
            "error": "Internal server error",
            "message": error_msg
        }

# Endpoint for mentor agent
@app.post("/mentor")
async def mentor(request: MentorRequest):
    """Get mentor guidance for technical questions"""
    logger.info("="*80)
    logger.info(f"MENTOR REQUEST RECEIVED")
    logger.info(f"  Query: {request.query[:100]}..." if len(request.query) > 100 else f"  Query: {request.query}")
    logger.info(f"  Context: {request.context}")
    logger.info("="*80)
    
    try:
        logger.debug("Getting agent orchestrator")
        orchestrator = get_agent_orchestrator()
        
        logger.info(f"Routing to mentor agent: query_length={len(request.query)}, context={request.context}")
        response = orchestrator.route_to_mentor_agent(request.query, request.context)
        
        if "error" in response:
            logger.error(f"Mentor agent returned error: {response.get('error')}")
            logger.error(f"Error message: {response.get('message', 'No message')}")
        else:
            logger.info("Mentor response generated successfully")
            if "mentor_response" in response:
                response_length = len(response["mentor_response"])
                logger.info(f"Mentor response length: {response_length} characters")
        
        return response
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception in mentor endpoint: {error_msg}")
        logger.exception("Full traceback:")
        return {
            "error": "Internal server error",
            "message": str(e)
        }

# Endpoint for assessment agent
@app.post("/assessment")
async def assessment(request: AssessmentRequest):
    """Assess user's approach and provide feedback with score"""
    logger.info("="*80)
    logger.info(f"ASSESSMENT REQUEST RECEIVED")
    logger.info(f"  Scenario: {request.scenario[:100]}..." if len(request.scenario) > 100 else f"  Scenario: {request.scenario}")
    logger.info("="*80)
    
    try:
        logger.debug("Getting agent orchestrator")
        orchestrator = get_agent_orchestrator()
        
        logger.info(f"Routing to assessment agent: scenario_length={len(request.scenario)}")
        response = orchestrator.route_to_assessment_agent(request.scenario)
        
        if "error" in response:
            logger.error(f"Assessment agent returned error: {response.get('error')}")
            logger.error(f"Error message: {response.get('message', 'No message')}")
        else:
            logger.info("Assessment completed successfully")
            if "score" in response:
                logger.info(f"Assessment score: {response.get('score')}")
            if "feedback" in response:
                feedback_length = len(response["feedback"])
                logger.info(f"Feedback length: {feedback_length} characters")
        
        return response
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception in assessment endpoint: {error_msg}")
        logger.exception("Full traceback:")
        return {
            "error": "Internal server error",
            "message": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "service": "AI Telecom Training Coach API"}
