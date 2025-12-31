#3_assessment
import streamlit as st
import requests

st.title("📊 Assessment & Feedback")

# Step 1: Topic Selection
topics = ["mml", "alarm_handling"]  # Example topics
selected_topic = st.selectbox("Select a Topic", topics)

# Step 2: Generate Questions (on Topic Selection)

if selected_topic:
    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            payload = {
                "topic": selected_topic
            }
            # Request to backend to generate questions for the selected topic
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/generate_questions", 
                    json=payload,
                    timeout=30  # Added: timeout for question generation
                )
                
                if response.status_code == 200:
                    questions_data = response.json()
                    if "questions" in questions_data:
                        st.session_state.questions = questions_data["questions"]
                        st.session_state.answers = {}  # Reset answers if new questions are generated
                        st.write("### Questions")
                        for i, question in enumerate(st.session_state.questions):
                            st.text_input(f"Question {i+1}: {question['question']}", key=f"answer_{i+1}")
                    else:
                        st.error("No questions returned for this topic.")
                else:
                    st.error(f"Failed to generate questions. Status code: {response.status_code}")
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            st.error(f"Error: {error_data['error']}")
                            if "message" in error_data:
                                st.info(f"💡 {error_data['message']}")
                    except:
                        st.error("Please try again later.")
            except requests.exceptions.ConnectionError:
                st.error("❌ **Backend not available!** Please ensure the backend server is running on http://127.0.0.1:8000")
                st.info("💡 Start the backend with: `./run_backend.sh`")
            except requests.exceptions.Timeout:
                st.error("⏱️ **Request timed out!** Please try again.")
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
                
# Step 3: User answers
if 'questions' in st.session_state:
    if st.button("Submit Assessment"):
        answers = {}
        for i, question in enumerate(st.session_state.questions):
            answer_key = f"answer_{i+1}"
            answer = st.session_state.get(answer_key, "")
            answers[i] = answer

        # Step 4: Send answers to backend for evaluation
        with st.spinner("Evaluating your responses..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/evaluate_assessment", 
                    json={"answers": answers},
                    timeout=180  # Increased to 180 seconds (3 minutes) - LLM evaluation can take 120-150 seconds
                )

                if response.status_code == 200:
                    data = response.json()
                    if "feedback" in data and "score" in data:
                        st.subheader("📝 Feedback")
                        st.markdown(data["feedback"])
                        st.metric("Competency Score", data["score"])
                        
                        # Track progress if user is logged in
                        if "username" in st.session_state and st.session_state.username:
                            try:
                                progress_payload = {
                                    "username": st.session_state.username,
                                    "activity_type": "assessment",
                                    "activity_data": {
                                        "topic": selected_topic,
                                        "score": data.get("score", 0),
                                        "num_questions": len(st.session_state.questions)
                                    }
                                }
                                progress_response = requests.post(
                                    "http://127.0.0.1:8000/user/progress/update",
                                    json=progress_payload,
                                    timeout=5
                                )
                                if progress_response.status_code == 200:
                                    st.success("✅ Assessment progress saved!")
                            except Exception as e:
                                # Don't show error to user, just log silently
                                pass
                        
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
                    st.error(f"Failed to evaluate assessment. Status code: {response.status_code}")
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            st.error(f"Error: {error_data['error']}")
                            if "message" in error_data:
                                st.info(f"💡 {error_data['message']}")
                    except:
                        st.error("Please try again later.")
            except requests.exceptions.ConnectionError:
                st.error("❌ **Backend not available!** Please ensure the backend server is running on http://127.0.0.1:8000")
                st.info("💡 Start the backend with: `./run_backend.sh`")
            except requests.exceptions.Timeout:
                st.error("⏱️ **Request timed out!** The LLM is taking longer than expected. Please try again.")
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
