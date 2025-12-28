

import streamlit as st
import requests

st.title("🤝 Mentor Agent")

# Input for user's technical query
user_query = st.text_area("Ask your technical question")

# Button to send the query to the Mentor Agent
if st.button("Ask Mentor"):
    if user_query:
        with st.spinner("Getting mentor guidance..."):
            response = requests.post("http://127.0.0.1:8000/mentor", json={"query": user_query, "context": "training"})
            
            if response.status_code == 200:
                data = response.json()
                # Check if response contains error or mentor response
                if "error" in data:
                    st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
                    if "message" in data:
                        st.info(f"💡 {data['message']}")
                elif "mentor_response" in data:
                    st.subheader("👩‍💻 Mentor Response")
                    st.markdown(data["mentor_response"])
                else:
                    st.warning("Unexpected response format from server.")
            else:
                st.error(f"Failed to fetch mentor response. Status code: {response.status_code}")
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        st.error(f"Error: {error_data['error']}")
                except:
                    st.error("Please try again later.")
    else:
        st.warning("Please enter your query before asking.")


