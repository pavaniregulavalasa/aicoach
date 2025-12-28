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

# Navigation section - Streamlit automatically creates sidebar navigation
st.markdown("---")
st.markdown("### 🚀 Available Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
        <h2>📚</h2>
        <h3>Training Agent</h3>
        <p>Get personalized training content</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
        <h2>🤝</h2>
        <h3>Mentor Agent</h3>
        <p>Get expert guidance & answers</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
        <h2>📊</h2>
        <h3>Assessment</h3>
        <p>Evaluate your competency</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.success("👈 **Navigate using the sidebar menu on the left!** Streamlit automatically creates navigation links for all pages in the `pages/` directory.")
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
