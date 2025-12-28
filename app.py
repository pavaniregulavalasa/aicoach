import streamlit as st
import requests

st.set_page_config(
    page_title="AI Coach",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Coach – Intelligent Training")
st.markdown("""
This application helps you get personalized training content based on your selected level. 
Choose your level and start your learning journey!
""")

# Navigation buttons on main page
st.markdown("---")
st.markdown("### 🚀 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📚 Training Agent", use_container_width=True, type="primary"):
        st.switch_page("pages/1_training.py")

with col2:
    if st.button("🤝 Mentor Agent", use_container_width=True):
        st.switch_page("pages/2_mentor.py")

with col3:
    if st.button("📊 Assessment", use_container_width=True):
        st.switch_page("pages/3_assessment.py")

st.markdown("---")

# Sidebar for Navigation
st.sidebar.header("Select Training Level")
level = st.sidebar.selectbox(
    "Select your Training Level",
    ["Beginner", "Intermediate", "Advanced"]
)

if st.sidebar.button("Start Training"):
    with st.spinner("Fetching personalized training..."):
        response = requests.post("http://127.0.0.1:8000/training", json={"level": level.lower(), "knowledge_base": "mml"})
        
        if response.status_code == 200:
            data = response.json()
            # Check if response contains error or training content
            if "error" in data:
                st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
                if "message" in data:
                    st.info(f"💡 {data['message']}")
            elif "training_content" in data:
                st.subheader(f"📚 {level} Level Training")
                st.markdown(data["training_content"])
            else:
                st.warning("Unexpected response format from server.")
        else:
            st.error(f"Failed to fetch training content. Status code: {response.status_code}")
            try:
                error_data = response.json()
                if "error" in error_data:
                    st.error(f"Error: {error_data['error']}")
            except:
                st.error("Please try again later.")
