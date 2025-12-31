# Profile page with dashboard and recommendations
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Profile - AI Coach",
    page_icon="👤",
    layout="wide"
)

# Check if user is logged in
if "username" not in st.session_state or not st.session_state.username:
    st.warning("⚠️ Please login first to view your profile.")
    st.info("👈 Go to the Login page from the sidebar")
    st.stop()

username = st.session_state.username

st.title(f"👤 Profile: {username}")

# Fetch user data
try:
    # Get profile
    profile_response = requests.get(
        f"http://127.0.0.1:8000/user/{username}/profile",
        timeout=5
    )
    
    # Get statistics
    stats_response = requests.get(
        f"http://127.0.0.1:8000/user/{username}/statistics",
        timeout=5
    )
    
    # Get recommendations
    rec_response = requests.get(
        f"http://127.0.0.1:8000/user/{username}/recommendations",
        timeout=5
    )
    
    profile = profile_response.json().get("profile", {}) if profile_response.status_code == 200 else {}
    stats = stats_response.json().get("statistics", {}) if stats_response.status_code == 200 else {}
    recommendations = rec_response.json().get("recommendations", []) if rec_response.status_code == 200 else []
    
except Exception as e:
    st.error(f"❌ Error loading profile data: {str(e)}")
    profile = {}
    stats = {}
    recommendations = []

# Dashboard Section
st.markdown("---")
st.subheader("📊 Learning Dashboard")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Training Sessions",
        stats.get("total_training_sessions", 0),
        help="Total number of training sessions completed"
    )

with col2:
    st.metric(
        "Assessments",
        stats.get("total_assessments", 0),
        help="Total number of assessments completed"
    )

with col3:
    st.metric(
        "Mentor Queries",
        stats.get("total_mentor_queries", 0),
        help="Total number of questions asked to mentor"
    )

with col4:
    training_time = stats.get("total_training_time_minutes", 0)
    st.metric(
        "Training Time",
        f"{training_time:.1f} min",
        help="Total time spent in training sessions"
    )

# Progress Section
st.markdown("---")
st.subheader("📈 Learning Progress")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Completed Levels")
    completed_levels = stats.get("completed_levels", {})
    if completed_levels:
        for level_key, count in completed_levels.items():
            kb, level = level_key.split("_", 1) if "_" in level_key else ("unknown", level_key)
            st.write(f"**{kb.upper()} - {level.title()}**: {count} session(s)")
    else:
        st.info("No training sessions completed yet. Start your learning journey!")

with col2:
    st.markdown("### Knowledge Bases Explored")
    kbs_used = stats.get("knowledge_bases_used", [])
    if kbs_used:
        for kb in kbs_used:
            st.success(f"✅ {kb.upper()}")
    else:
        st.info("No knowledge bases explored yet.")
    
    st.markdown("### Levels Attempted")
    levels = stats.get("levels_attempted", [])
    if levels:
        for level in levels:
            st.write(f"• {level.title()}")
    else:
        st.info("No levels attempted yet.")

# Recommendations Section
st.markdown("---")
st.subheader("💡 Personalized Recommendations")

if recommendations:
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
    
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", "low")
        priority_color = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")
        
        with st.expander(f"{priority_color} **{rec.get('title', 'Recommendation')}**", expanded=(priority == "high")):
            st.markdown(f"**Description:** {rec.get('description', '')}")
            st.markdown(f"**Action:** {rec.get('action', '')}")
else:
    st.info("🎉 Great job! You're on track with your learning. Keep exploring!")

# User Info Section
st.markdown("---")
st.subheader("ℹ️ Account Information")

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Username:** {profile.get('username', username)}")
    st.write(f"**Email:** {profile.get('email', 'N/A')}")

with col2:
    created_at = profile.get('created_at', '')
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            st.write(f"**Member Since:** {dt.strftime('%B %d, %Y')}")
        except:
            st.write(f"**Member Since:** {created_at}")
    
    last_activity = stats.get('last_activity')
    if last_activity:
        try:
            dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            st.write(f"**Last Activity:** {dt.strftime('%B %d, %Y at %I:%M %p')}")
        except:
            st.write(f"**Last Activity:** {last_activity}")

# Logout button
st.markdown("---")
if st.button("🚪 Logout", type="secondary"):
    st.session_state.username = None
    st.session_state.user_info = None
    st.success("Logged out successfully!")
    st.rerun()

