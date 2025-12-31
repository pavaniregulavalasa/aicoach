#1_training
import streamlit as st
import requests
from datetime import datetime

# Title for the Training page
st.title("📚 Training Agent")

st.markdown("---")

# Configuration section
st.subheader("⚙️ Configuration")

col1, col2 = st.columns(2)

with col1:
    level = st.selectbox(
        "Select your Training Level",
        ["beginner", "intermediate", "advanced", "architecture"],
        help="Choose the difficulty level for your training content"
    )

with col2:
    knowledge_base = st.selectbox(
        "Select the Knowledge Base",
        ["mml", "alarm_handling"],
        help="Choose the knowledge domain for training"
    )

st.markdown("---")

# Check if we have training content in session state
if "training_content" in st.session_state and st.session_state.training_content:
    # Display existing training content
    st.subheader(f"📖 {st.session_state.training_level.title()} Level Training on {st.session_state.training_kb.upper()}")
    st.markdown(st.session_state.training_content)
    
    # Download section
    st.markdown("---")
    st.subheader("📥 Download Training Content")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as PDF", use_container_width=True, key="download_pdf_btn"):
            with st.spinner("Generating PDF document..."):
                try:
                    doc_response = requests.post(
                        "http://127.0.0.1:8000/generate_document",
                        json={
                            "training_content": st.session_state.training_content,
                            "title": st.session_state.training_title,
                            "level": st.session_state.training_level,
                            "knowledge_base": st.session_state.training_kb,
                            "format_type": "pdf"
                        },
                        timeout=60
                    )
                    
                    if doc_response.status_code == 200:
                        # Check if response is actually a file (binary) or JSON error
                        content_type = doc_response.headers.get('content-type', '')
                        
                        # If it's JSON, it's an error response
                        if 'application/json' in content_type:
                            try:
                                error_data = doc_response.json()
                                st.error(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                                if "message" in error_data:
                                    st.info(f"💡 {error_data['message']}")
                            except:
                                st.error("Failed to generate PDF. Received JSON error response.")
                        else:
                            # It's a binary file
                            if len(doc_response.content) == 0:
                                st.error("❌ Generated PDF file is empty. Please try again.")
                            else:
                                # Validate PDF by checking magic bytes
                                if doc_response.content[:4] == b'%PDF':
                                    # Store in session state for download
                                    st.session_state.pdf_data = doc_response.content
                                    st.session_state.pdf_filename = f"{st.session_state.training_kb}_{st.session_state.training_level}_training_{datetime.now().strftime('%Y%m%d')}.pdf"
                                    st.success("✅ PDF generated successfully! Click the download button below.")
                                    st.rerun()
                                else:
                                    # Not a valid PDF, might be an error message
                                    try:
                                        error_text = doc_response.content.decode('utf-8')
                                        if 'error' in error_text.lower():
                                            st.error(f"❌ Error generating PDF: {error_text[:200]}")
                                        else:
                                            st.error("❌ Generated file is not a valid PDF. Please check backend logs.")
                                    except:
                                        st.error("❌ Generated file is not a valid PDF. Please check backend logs.")
                    else:
                        try:
                            error_data = doc_response.json()
                            st.error(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                            if "message" in error_data:
                                st.info(f"💡 {error_data['message']}")
                        except:
                            st.error(f"Failed to generate PDF. Status: {doc_response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ **Backend not available!** Please ensure the backend server is running.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ **Request timed out!** Please try again.")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.button("📊 Download as PowerPoint", use_container_width=True, key="download_ppt_btn"):
            with st.spinner("Generating PowerPoint presentation..."):
                try:
                    doc_response = requests.post(
                        "http://127.0.0.1:8000/generate_document",
                        json={
                            "training_content": st.session_state.training_content,
                            "title": st.session_state.training_title,
                            "level": st.session_state.training_level,
                            "knowledge_base": st.session_state.training_kb,
                            "format_type": "ppt"
                        },
                        timeout=60
                    )
                    
                    if doc_response.status_code == 200:
                        # Check if response is actually a file (binary) or JSON error
                        content_type = doc_response.headers.get('content-type', '')
                        
                        # If it's JSON, it's an error response
                        if 'application/json' in content_type:
                            try:
                                error_data = doc_response.json()
                                st.error(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                                if "message" in error_data:
                                    st.info(f"💡 {error_data['message']}")
                            except:
                                st.error("Failed to generate PowerPoint. Received JSON error response.")
                        else:
                            # It's a binary file
                            if len(doc_response.content) == 0:
                                st.error("❌ Generated PowerPoint file is empty. Please try again.")
                            else:
                                # Validate PPTX by checking magic bytes (ZIP format)
                                if doc_response.content[:2] == b'PK':
                                    # Store in session state for download
                                    st.session_state.ppt_data = doc_response.content
                                    st.session_state.ppt_filename = f"{st.session_state.training_kb}_{st.session_state.training_level}_training_{datetime.now().strftime('%Y%m%d')}.pptx"
                                    st.success("✅ PowerPoint generated successfully! Click the download button below.")
                                    st.rerun()
                                else:
                                    # Not a valid PPTX, might be an error message
                                    try:
                                        error_text = doc_response.content.decode('utf-8')
                                        if 'error' in error_text.lower():
                                            st.error(f"❌ Error generating PowerPoint: {error_text[:200]}")
                                        else:
                                            st.error("❌ Generated file is not a valid PowerPoint. Please check backend logs.")
                                    except:
                                        st.error("❌ Generated file is not a valid PowerPoint. Please check backend logs.")
                    else:
                        try:
                            error_data = doc_response.json()
                            st.error(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                            if "message" in error_data:
                                st.info(f"💡 {error_data['message']}")
                        except:
                            st.error(f"Failed to generate PowerPoint. Status: {doc_response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ **Backend not available!** Please ensure the backend server is running.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ **Request timed out!** Please try again.")
                except Exception as e:
                    st.error(f"❌ Error generating PowerPoint: {str(e)}")
    
    # Show download buttons if files are ready
    if "pdf_data" in st.session_state:
        st.markdown("---")
        st.download_button(
            label="⬇️ Download PDF File",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            use_container_width=True,
            key="pdf_download"
        )
    
    if "ppt_data" in st.session_state:
        st.markdown("---")
        st.download_button(
            label="⬇️ Download PowerPoint File",
            data=st.session_state.ppt_data,
            file_name=st.session_state.ppt_filename,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
            key="ppt_download"
        )
    
    st.markdown("---")
    if st.button("🔄 Generate New Training Content", use_container_width=True):
        # Clear session state to allow new generation
        if "training_content" in st.session_state:
            del st.session_state.training_content
        if "pdf_data" in st.session_state:
            del st.session_state.pdf_data
        if "ppt_data" in st.session_state:
            del st.session_state.ppt_data
        st.rerun()

# Button to start training
if st.button("Start Training"):
    with st.spinner("Fetching personalized training content..."):
        # Prepare the payload to send to the backend
        payload = {
            "knowledge_base": knowledge_base,
            "level": level.lower()
        }

        # Send the request to the backend with timeout and error handling
        try:
            response = requests.post(
                "http://127.0.0.1:8000/training", 
                json=payload,
                timeout=450  # Increased to 450 seconds (7.5 minutes) - LLM can take 300-400 seconds, with buffer
            )
            
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
                    # Store content in session state for download
                    st.session_state.training_content = data["training_content"]
                    st.session_state.training_title = f"{knowledge_base.upper()} - {level.title()} Training"
                    st.session_state.training_level = level
                    st.session_state.training_kb = knowledge_base
                    
                    # Clear any previous download data
                    if "pdf_data" in st.session_state:
                        del st.session_state.pdf_data
                    if "ppt_data" in st.session_state:
                        del st.session_state.ppt_data
                    
                    # Track progress if user is logged in
                    if "username" in st.session_state and st.session_state.username:
                        try:
                            progress_payload = {
                                "username": st.session_state.username,
                                "activity_type": "training",
                                "activity_data": {
                                    "level": level,
                                    "knowledge_base": knowledge_base,
                                    "duration": 0
                                }
                            }
                            progress_response = requests.post(
                                "http://127.0.0.1:8000/user/progress/update",
                                json=progress_payload,
                                timeout=5
                            )
                            # Don't show error to user, just log silently
                        except Exception as e:
                            # Don't show error to user, just log silently
                            pass
                    
                    st.success("✅ Training content generated successfully!")
                    st.rerun()  # Rerun to show the content and download buttons
                else:
                    st.warning("Unexpected response format from server.")
            else:
                st.error(f"Failed to fetch training content. Status code: {response.status_code}")
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
            st.error("⏱️ **Request timed out!** The LLM is taking longer than expected. Please try again or check if the backend is responsive.")
        except Exception as e:
            st.error(f"❌ **Error:** {str(e)}")


