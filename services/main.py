import logging
import sys
import time
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from services.agent_orchestrator import AgentOrchestrator
from services.user_service import (
    authenticate_user, get_user_profile, get_user_progress,
    update_user_progress, get_user_statistics, get_recommendations
)
from services.document_generator import generate_document
from fastapi.responses import FileResponse, StreamingResponse

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

class MentorRequest(BaseModel):
    query: str  # User's technical question
    context: str = "training"  # Context for the query

class AssessmentRequest(BaseModel):
    scenario: str  # User's approach to the scenario

class TopicRequest(BaseModel):
    topic: str  # Topic for question generation

class EvaluateAssessmentRequest(BaseModel):
    answers: dict  # Dictionary of question indices to answers

class LoginRequest(BaseModel):
    username: str
    password: str

class DocumentGenerationRequest(BaseModel):
    training_content: str
    title: str
    level: str
    knowledge_base: str
    format_type: str = "pdf"  # "pdf" or "ppt"

class ProgressUpdateRequest(BaseModel):
    username: str
    activity_type: str  # 'training', 'assessment', 'mentor'
    activity_data: dict

# Endpoint to request training from the training agent
@app.post("/training")
async def training(request: TrainingRequest):
    """Generate training content based on level and knowledge base"""
    request_start = time.time()
    logger.info("="*80)
    logger.info(f"🌐 [API] TRAINING REQUEST RECEIVED")
    logger.info(f"  Level: {request.level}")
    logger.info(f"  Knowledge Base: {request.knowledge_base}")
    logger.info(f"⏱️  [TIMING] Request received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    try:
        logger.debug("Getting agent orchestrator")
        orchestrator = get_agent_orchestrator()
        
        logger.info(f"🔄 [API] Routing to training agent: level={request.level}, kb={request.knowledge_base}")
        routing_start = time.time()
        response = orchestrator.route_to_training_agent(
            request.level, 
            request.knowledge_base
        )
        routing_elapsed = time.time() - routing_start
        
        if "error" in response:
            logger.error(f"❌ [API] Training agent returned error: {response.get('error')}")
            logger.error(f"❌ [API] Error message: {response.get('message', 'No message')}")
        else:
            logger.info("✅ [API] Training content generated successfully")
            logger.debug(f"Response keys: {list(response.keys())}")
            if "training_content" in response:
                content_length = len(response["training_content"])
                logger.info(f"📊 [API] Training content length: {content_length} characters")
        
        request_elapsed = time.time() - request_start
        logger.info("="*80)
        logger.info(f"⏱️  [TIMING] Total API request time: {request_elapsed:.2f} seconds ({request_elapsed/60:.2f} minutes)")
        logger.info(f"⏱️  [TIMING] Agent processing time: {routing_elapsed:.2f} seconds")
        logger.info("="*80)
        
        # Track progress if username is provided (optional for now, can be added to request later)
        # This will be handled by frontend after successful response
        
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
            "message": error_msg
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
            "message": error_msg
        }

# Endpoint for generating questions
@app.post("/generate_questions")
async def generate_questions(request: TopicRequest):
    """Generate questions for a given topic"""
    logger.info("="*80)
    logger.info(f"GENERATE QUESTIONS REQUEST RECEIVED")
    logger.info(f"  Topic: {request.topic}")
    logger.info("="*80)
    
    try:
        # Import here to avoid circular dependencies
        from services.generate_questions import question_bank
        import random
        
        questions = question_bank.get(request.topic, [])
        
        if not questions:
            logger.warning(f"No questions available for topic: {request.topic}")
            return {
                "error": "No questions available",
                "message": f"No questions available for topic '{request.topic}'. Available topics: {list(question_bank.keys())}"
            }
        
        # Shuffle questions for variety
        random.shuffle(questions)
        
        logger.info(f"Generated {len(questions)} questions for topic: {request.topic}")
        return {"questions": questions}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception in generate_questions endpoint: {error_msg}")
        logger.exception("Full traceback:")
        return {
            "error": "Internal server error",
            "message": error_msg
        }

# Endpoint for evaluating assessment answers
@app.post("/evaluate_assessment")
async def evaluate_assessment(request: EvaluateAssessmentRequest):
    """Evaluate user's answers and provide feedback with score"""
    logger.info("="*80)
    logger.info(f"EVALUATE ASSESSMENT REQUEST RECEIVED")
    logger.info(f"  Number of answers: {len(request.answers)}")
    logger.info("="*80)
    
    try:
        logger.debug("Getting agent orchestrator")
        orchestrator = get_agent_orchestrator()
        
        # Convert answers dict to a scenario string for assessment
        # Format: "Question 1: [answer1]\nQuestion 2: [answer2]..."
        scenario_parts = []
        for idx, answer in request.answers.items():
            scenario_parts.append(f"Question {idx+1}: {answer}")
        
        scenario = "\n".join(scenario_parts)
        
        logger.info(f"Routing to assessment agent: scenario_length={len(scenario)}")
        response = orchestrator.route_to_assessment_agent(scenario)
        
        if "error" in response:
            logger.error(f"Assessment agent returned error: {response.get('error')}")
            logger.error(f"Error message: {response.get('message', 'No message')}")
        else:
            logger.info("Assessment evaluation completed successfully")
            if "score" in response:
                logger.info(f"Assessment score: {response.get('score')}")
            if "feedback" in response:
                feedback_length = len(response["feedback"])
                logger.info(f"Feedback length: {feedback_length} characters")
        
        return response
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception in evaluate_assessment endpoint: {error_msg}")
        logger.exception("Full traceback:")
        return {
            "error": "Internal server error",
            "message": error_msg
        }

# User authentication and profile endpoints
@app.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user with username and password"""
    logger.info(f"Login attempt for username: {request.username}")
    
    user = authenticate_user(request.username, request.password)
    
    if user:
        logger.info(f"Login successful for: {request.username}")
        return {
            "success": True,
            "user": user,
            "message": "Login successful"
        }
    else:
        logger.warning(f"Login failed for: {request.username}")
        return {
            "success": False,
            "message": "Invalid username or password"
        }

@app.get("/user/{username}/profile")
async def get_profile(username: str):
    """Get user profile information"""
    logger.info(f"Getting profile for: {username}")
    profile = get_user_profile(username)
    
    if profile:
        return {"success": True, "profile": profile}
    else:
        return {"success": False, "message": "User not found"}

@app.get("/user/{username}/progress")
async def get_progress(username: str):
    """Get user's learning progress"""
    logger.info(f"Getting progress for: {username}")
    progress = get_user_progress(username)
    return {"success": True, "progress": progress}

@app.get("/user/{username}/statistics")
async def get_statistics(username: str):
    """Get user statistics for dashboard"""
    logger.info(f"Getting statistics for: {username}")
    stats = get_user_statistics(username)
    return {"success": True, "statistics": stats}

@app.get("/user/{username}/recommendations")
async def get_user_recommendations(username: str):
    """Get personalized learning recommendations"""
    logger.info(f"Getting recommendations for: {username}")
    recommendations = get_recommendations(username)
    return {"success": True, "recommendations": recommendations}

@app.post("/user/progress/update")
async def update_progress(request: ProgressUpdateRequest):
    """Update user's learning progress"""
    logger.info(f"Updating progress for {request.username}: {request.activity_type}")
    update_user_progress(request.username, request.activity_type, request.activity_data)
    return {"success": True, "message": "Progress updated successfully"}

# Document generation endpoint
@app.post("/generate_document")
async def generate_training_document(request: DocumentGenerationRequest):
    """Generate PDF or PPT document from training content"""
    logger.info("="*80)
    logger.info(f"🌐 [API] DOCUMENT GENERATION REQUEST")
    logger.info(f"  Format: {request.format_type}")
    logger.info(f"  Level: {request.level}")
    logger.info(f"  Knowledge Base: {request.knowledge_base}")
    logger.info(f"  Title: {request.title}")
    logger.info("="*80)
    
    try:
        # Generate document
        output_path = generate_document(
            training_content=request.training_content,
            title=request.title,
            level=request.level,
            knowledge_base=request.knowledge_base,
            format_type=request.format_type,
            output_dir="generated_docs"
        )
        
        if output_path and os.path.exists(output_path):
            # Verify file is not empty
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                logger.error(f"Generated document is empty: {output_path}")
                return {
                    "error": "Document Generation Error",
                    "message": "Generated document is empty. Please try again."
                }
            
            logger.info(f"✅ Document generated: {output_path} ({file_size} bytes)")
            
            # Read file content to ensure it's valid
            try:
                with open(output_path, 'rb') as f:
                    file_content = f.read()
                
                # Verify PDF magic bytes
                if request.format_type.lower() == "pdf":
                    if not file_content.startswith(b'%PDF'):
                        logger.error(f"Generated file is not a valid PDF: {output_path}")
                        return {
                            "error": "Document Generation Error",
                            "message": "Generated PDF file is corrupted. Please try again."
                        }
                # Verify PPTX magic bytes (ZIP format)
                elif request.format_type.lower() in ["ppt", "pptx"]:
                    if not file_content.startswith(b'PK'):
                        logger.error(f"Generated file is not a valid PPTX: {output_path}")
                        return {
                            "error": "Document Generation Error",
                            "message": "Generated PowerPoint file is corrupted. Please try again."
                        }
                
                # Return file using StreamingResponse for better handling
                from io import BytesIO
                
                return StreamingResponse(
                    BytesIO(file_content),
                    media_type="application/pdf" if request.format_type.lower() == "pdf" else "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    headers={"Content-Disposition": f'attachment; filename="{os.path.basename(output_path)}"'}
                )
            except Exception as e:
                logger.error(f"Error reading generated file: {str(e)}")
                logger.exception("Full traceback:")
                return {
                    "error": "Document Generation Error",
                    "message": f"Error reading generated file: {str(e)}"
                }
        else:
            logger.error("Failed to generate document - output_path is None or file doesn't exist")
            return {
                "error": "Document Generation Error",
                "message": "Failed to generate document. Please check if required libraries are installed (reportlab for PDF, python-pptx for PPT)."
            }
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        logger.exception("Full traceback:")
        return {
            "error": "Document Generation Error",
            "message": f"Failed to generate document: {str(e)}"
        }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "service": "AI Telecom Training Coach API"}
