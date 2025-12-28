from fastapi import FastAPI
from pydantic import BaseModel
from services.agent_orchestrator import AgentOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title="AI Telecom Training Coach API",
    description="Backend API for AI-powered telecom training platform",
    version="1.0.0"
)

# Agent Orchestrator instance (lazy initialization to avoid startup errors)
agent_orchestrator = None

def get_agent_orchestrator():
    """Lazy initialization of agent orchestrator"""
    global agent_orchestrator
    if agent_orchestrator is None:
        agent_orchestrator = AgentOrchestrator()
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
    try:
        orchestrator = get_agent_orchestrator()
        response = orchestrator.route_to_training_agent(
            request.level, 
            request.knowledge_base, 
            request.topic
        )
        return response
    except FileNotFoundError as e:
        return {
            "error": str(e),
            "message": "Please run services/rag.py first to create FAISS indexes"
        }
    except Exception as e:
        error_msg = str(e)
        # Provide more specific error messages for connection issues
        if "Connection" in error_msg or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
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
    try:
        orchestrator = get_agent_orchestrator()
        response = orchestrator.route_to_mentor_agent(request.query, request.context)
        return response
    except Exception as e:
        return {
            "error": "Internal server error",
            "message": str(e)
        }

# Endpoint for assessment agent
@app.post("/assessment")
async def assessment(request: AssessmentRequest):
    """Assess user's approach and provide feedback with score"""
    try:
        orchestrator = get_agent_orchestrator()
        response = orchestrator.route_to_assessment_agent(request.scenario)
        return response
    except Exception as e:
        return {
            "error": "Internal server error",
            "message": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Telecom Training Coach API"}
