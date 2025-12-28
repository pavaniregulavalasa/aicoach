
import streamlit as st
import requests

# Title for the Training page
st.title("📚 Training Agent")

# Sidebar for selecting level and knowledge base
level = st.selectbox(
    "Select your Training Level",
    ["Beginner", "Intermediate", "Advanced", "Architecture"]
)

knowledge_base = st.selectbox(
    "Select the Knowledge Base",
    ["mml", "alarm_handling"]
)

# Optional: Topic input (for more specific training or doubt clearing)
topic = st.text_input("Enter a specific topic for doubt clearing (Optional)")

# Button to start training
if st.button("Start Training"):
    with st.spinner("Fetching personalized training content..."):
        # Prepare the payload to send to the backend
        payload = {
            "knowledge_base": knowledge_base,
            "level": level.lower(),
            "topic": topic
        }

        # Send the request to the backend
        response = requests.post("http://127.0.0.1:8000/training", json=payload)

        if response.status_code == 200:
            data = response.json()
            # Check if response contains error or training content
            if "error" in data:
                st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
                if "message" in data:
                    st.info(f"💡 {data['message']}")
                    st.markdown("""
                    **To fix this:**
                    1. Ensure you have PDF documents in the `./knowledge/` directory
                    2. Run: `python services/rag.py` to create FAISS indexes
                    """)
            elif "training_content" in data:
                st.subheader(f"📖 {level} Level Training on {knowledge_base.upper()}")
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

