#generate_questions
from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class TopicRequest(BaseModel):
    topic: str

# Sample question bank (You can replace this with dynamic AI-based generation logic)
question_bank = {
    "mml": [
        {"question": "What does MML stand for"},
        {"question": "Explain ADP protocol"},
        {"question": "What are the possible states for a mml session"},
        {"question":"Explain how the device is seized"}
    ],
    "alarm_handling": [
        {"question": "Explain how the alarm handling is done on APG"},
        {"question": "Which are the main functional blocks involved in alarm handling"},
        {"question": "which is the command used to view the alarms on APG"}
    ]
}

@app.post("/generate_questions")
async def generate_questions(request: TopicRequest):
    topic = request.topic
    questions = question_bank.get(topic, [])
    
    if not questions:
        return {"error": "No questions available for this topic."}
    
    # Shuffle questions for variety (optional)
    random.shuffle(questions)
    
    return {"questions": questions}

