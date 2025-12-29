import streamlit as st
import requests

st.title("📊 Assessment & Feedback")

# User input for scenario-based assessment
scenario = st.text_area("Describe your approach to the scenario:")

if st.button("Submit Assessment"):
    if scenario:
        with st.spinner("Evaluating your approach..."):
            try:
                response = requests.post("http://127.0.0.1:8000/assessment", json={"scenario": scenario}, timeout=180)
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if response contains error or assessment data
                    if "error" in data:
                        st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
                        if "message" in data:
                            st.info(f"💡 {data['message']}")
                    elif "feedback" in data and "score" in data:
                        st.subheader("📝 Feedback")
                        st.markdown(data["feedback"])
                        st.metric("Competency Score", data["score"])
                        # Show additional details if available
                        if "strengths" in data and data["strengths"]:
                            with st.expander("✅ Strengths"):
                                for strength in data["strengths"]:
                                    st.write(f"• {strength}")
                        if "improvements" in data and data["improvements"]:
                            with st.expander("📈 Areas for Improvement"):
                                for improvement in data["improvements"]:
                                    st.write(f"• {improvement}")
                    else:
                        st.warning("Unexpected response format from server.")
                else:
                    st.error(f"Failed to submit assessment. Status code: {response.status_code}")
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            st.error(f"Error: {error_data['error']}")
                    except:
                        st.error("Please try again later.")
            except requests.exceptions.ConnectionError:
                st.error("❌ **Backend not available!** Please ensure the backend server is running on http://127.0.0.1:8000")
                st.info("💡 Start the backend with: `./run_backend.sh`")
            except requests.exceptions.Timeout:
                st.error("⏱️ **Request timed out!** The LLM is taking longer than expected. Please try again or check if the backend is responsive.")
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
    else:
        st.warning("Please provide your approach to the scenario.")


