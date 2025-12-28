from services.ai_coach import ComprehensiveTrainingCoach
import services.ai_coach

retrieve_training_content = services.ai_coach.retrieve_training_content
LLM = services.ai_coach.LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class AssessmentAgent:
    """Agent that assesses user's approach and provides feedback with scores"""
    
    def __init__(self):
        # Try to initialize coach, but don't fail if indexes are missing
        try:
            self.comprehensive_coach = ComprehensiveTrainingCoach()
        except FileNotFoundError:
            # Coach not available, but we can still provide assessment
            self.comprehensive_coach = None
    
    def handle_request(self, scenario: str):
        """
        Assess user's approach to a scenario and provide feedback
        
        Args:
            scenario: User's description of their approach to a scenario
        
        Returns:
            Dictionary with feedback and score
        """
        # Retrieve relevant content for assessment context
        knowledge_bases = ["mml", "alarm_handling"]
        relevant_content = []
        
        for kb in knowledge_bases:
            try:
                content = retrieve_training_content.invoke({
                    "knowledge_base": kb,
                    "level": "advanced",
                    "topic": scenario
                })
                if content and not content.startswith("❌"):
                    relevant_content.append(f"=== {kb.upper()} KNOWLEDGE BASE ===\n{content}\n")
            except Exception:
                continue
        
        # Generate assessment
        prompt = ChatPromptTemplate.from_template("""
You are an **Expert Telecom Training Assessor** evaluating a learner's approach to a technical scenario.

**USER'S APPROACH**: {scenario}

**RELEVANT KNOWLEDGE BASE CONTENT**:
{knowledge_content}

**YOUR TASK**: Provide comprehensive assessment with:
1. **Strengths** - What the learner did well
2. **Areas for Improvement** - Specific gaps or issues
3. **Technical Accuracy** - Correctness of approach, commands, procedures
4. **Best Practices Alignment** - How well it follows industry standards
5. **Risk Assessment** - Potential issues or risks in the approach
6. **Recommendations** - Specific actionable improvements

**SCORING CRITERIA** (0-100):
- Technical Accuracy: 30 points
- Best Practices: 25 points
- Completeness: 20 points
- Risk Awareness: 15 points
- Innovation/Problem-Solving: 10 points

**OUTPUT FORMAT** (JSON):
{{
    "feedback": "Detailed feedback text covering all assessment points",
    "score": <integer 0-100>,
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "technical_notes": "Specific technical observations"
}}

**RESPONSE** (JSON only, no markdown):
        """)
        
        chain = prompt | LLM | StrOutputParser()
        
        knowledge_content = "\n\n".join(relevant_content) if relevant_content else "No specific knowledge base content found. Assess based on general telecom best practices."
        
        assessment_text = chain.invoke({
            "scenario": scenario,
            "knowledge_content": knowledge_content
        })
        
        # Try to parse JSON response, fallback to text if parsing fails
        try:
            # Clean up the response - remove markdown code blocks if present
            cleaned = assessment_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            assessment_data = json.loads(cleaned)
            
            # Ensure required fields
            if "score" not in assessment_data:
                assessment_data["score"] = 75  # Default score
            if "feedback" not in assessment_data:
                assessment_data["feedback"] = assessment_text
            
            return {
                "feedback": assessment_data.get("feedback", assessment_text),
                "score": assessment_data.get("score", 75),
                "strengths": assessment_data.get("strengths", []),
                "improvements": assessment_data.get("improvements", []),
                "technical_notes": assessment_data.get("technical_notes", "")
            }
        except (json.JSONDecodeError, KeyError):
            # Fallback: extract score from text or use default
            score = 75
            if "score" in assessment_text.lower():
                # Try to extract number
                import re
                score_match = re.search(r'score["\']?\s*:\s*(\d+)', assessment_text, re.IGNORECASE)
                if score_match:
                    score = int(score_match.group(1))
            
            return {
                "feedback": assessment_text,
                "score": score,
                "strengths": [],
                "improvements": [],
                "technical_notes": ""
            }

