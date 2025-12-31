# Login page (0_ prefix makes it appear first in Streamlit navigation)
import streamlit as st
import requests

st.set_page_config(
    page_title="Login - AI Coach",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Login to AI Coach")

# Check if user is already logged in
if "username" in st.session_state and st.session_state.username:
    st.success(f"✅ Already logged in as: **{st.session_state.username}**")
    if st.button("Logout"):
        st.session_state.username = None
        st.session_state.user_info = None
        st.rerun()
    st.markdown("---")
    st.info("👈 Use the sidebar to navigate to other pages")

else:
    # Login form
    with st.form("login_form"):
        st.markdown("### Enter your credentials")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            submit_button = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="padding-top: 10px;">
            <small>💡 <strong>Demo Credentials:</strong><br>
            Username: <code>admin</code> | Password: <code>admin123</code><br>
            Username: <code>user1</code> | Password: <code>password123</code></small>
            </div>
            """, unsafe_allow_html=True)
    
    if submit_button:
        if not username or not password:
            st.error("❌ Please enter both username and password")
        else:
            with st.spinner("Logging in..."):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8000/auth/login",
                        json={"username": username, "password": password},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            # Store user info in session state
                            st.session_state.username = username
                            st.session_state.user_info = data.get("user", {})
                            st.success(f"✅ Welcome, **{username}**!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {data.get('message', 'Login failed')}")
                    else:
                        st.error(f"❌ Login failed. Status code: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ **Backend not available!** Please ensure the backend server is running.")
                    st.info("💡 Start the backend with: `./run_backend.sh`")
                except requests.exceptions.Timeout:
                    st.error("⏱️ **Request timed out!** Please try again.")
                except Exception as e:
                    st.error(f"❌ **Error:** {str(e)}")

