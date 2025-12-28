# agent router , backend hook
def call_training_agent(**kwargs):
    # Placeholder for backend / LLM / RAG call
    if kwargs.get("evaluate"):
        return "Good understanding. Consider revisiting edge cases."

    if kwargs.get("assess"):
        return {
            "feedback": "Strong debugging approach, improve root cause isolation.",
            "score": 82
        }

    return """
### Training Module: Product Architecture
- Overview of system components
- Data flow explanation
- Common pitfalls
"""


def call_mentor_agent(query, context):
    return f"""
**Mentor Insight:**
Here’s how a senior engineer would approach this:

- Understand the requirement
- Check related Jira tickets
- Review recent commits
- Validate assumptions

Best practice: always verify logs first.
"""
