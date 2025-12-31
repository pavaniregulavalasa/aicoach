"""
User Service - Handles user authentication, profiles, and progress tracking
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# User data storage (simple JSON file for now)
USER_DATA_FILE = "data/users.json"
USER_PROGRESS_FILE = "data/user_progress.json"

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Default dummy users (for development)
DEFAULT_USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # Dummy password
        "email": "admin@example.com",
        "created_at": datetime.now().isoformat()
    },
    "user1": {
        "username": "user1",
        "password": "password123",  # Dummy password
        "email": "user1@example.com",
        "created_at": datetime.now().isoformat()
    }
}

def load_users() -> Dict:
    """Load users from JSON file, create default if doesn't exist"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading users: {e}, using defaults")
            return DEFAULT_USERS.copy()
    else:
        # Create default users file
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS.copy()

def save_users(users: Dict):
    """Save users to JSON file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

def load_user_progress() -> Dict:
    """Load user progress from JSON file"""
    if os.path.exists(USER_PROGRESS_FILE):
        try:
            with open(USER_PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading progress: {e}, using empty dict")
            return {}
    return {}

def save_user_progress(progress: Dict):
    """Save user progress to JSON file"""
    try:
        with open(USER_PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving progress: {e}")

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password"""
    users = load_users()
    
    if username in users and users[username]["password"] == password:
        # Return user info without password
        user_info = users[username].copy()
        user_info.pop("password", None)
        logger.info(f"User authenticated: {username}")
        return user_info
    else:
        logger.warning(f"Authentication failed for username: {username}")
        return None

def get_user_profile(username: str) -> Optional[Dict]:
    """Get user profile information"""
    users = load_users()
    if username in users:
        user_info = users[username].copy()
        user_info.pop("password", None)
        return user_info
    return None

def get_user_progress(username: str) -> Dict:
    """Get user's learning progress"""
    progress_data = load_user_progress()
    return progress_data.get(username, {
        "username": username,
        "training_sessions": [],
        "assessments": [],
        "mentor_queries": [],
        "completed_levels": {},
        "total_training_time": 0,
        "last_activity": None
    })

def update_user_progress(username: str, activity_type: str, activity_data: Dict):
    """Update user's learning progress"""
    progress_data = load_user_progress()
    
    if username not in progress_data:
        progress_data[username] = {
            "username": username,
            "training_sessions": [],
            "assessments": [],
            "mentor_queries": [],
            "completed_levels": {},
            "total_training_time": 0,
            "last_activity": None
        }
    
    # Add activity to appropriate list
    activity = {
        **activity_data,
        "timestamp": datetime.now().isoformat()
    }
    
    if activity_type == "training":
        progress_data[username]["training_sessions"].append(activity)
        # Track completed levels
        level = activity_data.get("level", "")
        knowledge_base = activity_data.get("knowledge_base", "")
        key = f"{knowledge_base}_{level}"
        if key not in progress_data[username]["completed_levels"]:
            progress_data[username]["completed_levels"][key] = 0
        progress_data[username]["completed_levels"][key] += 1
    elif activity_type == "assessment":
        progress_data[username]["assessments"].append(activity)
    elif activity_type == "mentor":
        progress_data[username]["mentor_queries"].append(activity)
    
    # Update total training time if provided
    if "duration" in activity_data:
        progress_data[username]["total_training_time"] += activity_data["duration"]
    
    # Update last activity
    progress_data[username]["last_activity"] = datetime.now().isoformat()
    
    save_user_progress(progress_data)
    logger.info(f"Updated progress for {username}: {activity_type}")

def get_user_statistics(username: str) -> Dict:
    """Get user statistics for dashboard"""
    progress = get_user_progress(username)
    
    stats = {
        "total_training_sessions": len(progress.get("training_sessions", [])),
        "total_assessments": len(progress.get("assessments", [])),
        "total_mentor_queries": len(progress.get("mentor_queries", [])),
        "completed_levels": progress.get("completed_levels", {}),
        "total_training_time_minutes": progress.get("total_training_time", 0) / 60,
        "last_activity": progress.get("last_activity"),
        "knowledge_bases_used": set(),
        "levels_attempted": set()
    }
    
    # Analyze training sessions
    for session in progress.get("training_sessions", []):
        kb = session.get("knowledge_base", "")
        level = session.get("level", "")
        if kb:
            stats["knowledge_bases_used"].add(kb)
        if level:
            stats["levels_attempted"].add(level)
    
    # Convert sets to lists for JSON serialization
    stats["knowledge_bases_used"] = list(stats["knowledge_bases_used"])
    stats["levels_attempted"] = list(stats["levels_attempted"])
    
    return stats

def get_recommendations(username: str) -> List[Dict]:
    """Generate personalized learning recommendations"""
    progress = get_user_progress(username)
    stats = get_user_statistics(username)
    
    recommendations = []
    
    # Check if user hasn't started training
    if stats["total_training_sessions"] == 0:
        recommendations.append({
            "type": "start_training",
            "priority": "high",
            "title": "Start Your Learning Journey",
            "description": "Begin with beginner-level training to build a strong foundation.",
            "action": "Go to Training Agent and select Beginner level"
        })
        return recommendations
    
    # Check for level progression
    levels = ["beginner", "intermediate", "advanced", "architecture"]
    completed = stats.get("completed_levels", {})
    
    # Find next level to recommend
    for i, level in enumerate(levels):
        level_count = sum(1 for k in completed.keys() if level in k)
        if level_count == 0 and i > 0:
            prev_level = levels[i-1]
            prev_count = sum(1 for k in completed.keys() if prev_level in k)
            if prev_count > 0:
                recommendations.append({
                    "type": "level_progression",
                    "priority": "high",
                    "title": f"Progress to {level.title()} Level",
                    "description": f"You've completed {prev_level} level training. Ready to advance?",
                    "action": f"Try {level.title()} level training"
                })
                break
    
    # Check knowledge base coverage
    knowledge_bases = ["mml", "alarm_handling"]
    used_kbs = set(stats.get("knowledge_bases_used", []))
    
    for kb in knowledge_bases:
        if kb not in used_kbs:
            recommendations.append({
                "type": "knowledge_base",
                "priority": "medium",
                "title": f"Explore {kb.upper()} Knowledge Base",
                "description": f"You haven't explored {kb.upper()} yet. Expand your knowledge!",
                "action": f"Try training with {kb.upper()} knowledge base"
            })
    
    # Check assessment completion
    if stats["total_assessments"] == 0:
        recommendations.append({
            "type": "assessment",
            "priority": "medium",
            "title": "Take an Assessment",
            "description": "Test your knowledge with an assessment to see your progress.",
            "action": "Go to Assessment & Feedback page"
        })
    
    # Check mentor usage
    if stats["total_mentor_queries"] == 0:
        recommendations.append({
            "type": "mentor",
            "priority": "low",
            "title": "Ask the Mentor",
            "description": "Get expert guidance by asking questions to the Mentor Agent.",
            "action": "Try the Mentor Agent for personalized help"
        })
    
    return recommendations

