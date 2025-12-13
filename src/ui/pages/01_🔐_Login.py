"""Login and Registration page for NLP Feedback Analysis System."""

import streamlit as st
from src.ui.utils.auth import (
    init_session_state,
    login_user,
    register_user,
    is_authenticated,
    logout_user
)

# Page configuration
st.set_page_config(
    page_title="Login - NLP Feedback Analysis",
    page_icon="🔐",
    layout="centered"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .login-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="login-header">', unsafe_allow_html=True)
st.title("🔐 NLP Feedback Analysis System")
st.markdown("### User Authentication")
st.markdown('</div>', unsafe_allow_html=True)

# Check if already authenticated
if is_authenticated():
    st.success(f"✅ You are already logged in as **{st.session_state.user_info.get('username', 'User')}**")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()

    st.divider()

    # User info
    st.subheader("👤 Your Account")

    user_info = st.session_state.user_info

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Username", user_info.get('username', 'N/A'))
        st.metric("Email", user_info.get('email', 'N/A'))

    with col2:
        st.metric("Full Name", user_info.get('full_name', 'Not set'))
        st.metric("Account Status", "Active" if user_info.get('is_active') else "Inactive")

    st.info("💡 **Tip:** Navigate to other pages from the sidebar to start analyzing feedback!")

else:
    # Tabs for Login and Register
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    # Login Tab
    with tab1:
        st.markdown("### Sign in to your account")

        with st.form("login_form"):
            username = st.text_input(
                "Username or Email",
                placeholder="Enter your username or email",
                help="You can use either your username or email address"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.form_submit_button("🔓 Login", use_container_width=True)

            if submit_button:
                if not username or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    with st.spinner("Logging in..."):
                        result = login_user(username, password)

                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            # Wait a moment before rerun
                            st.info("Redirecting to dashboard...")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")

        st.divider()
        st.caption("Don't have an account? Switch to the **Register** tab above")

    # Register Tab
    with tab2:
        st.markdown("### Create a new account")

        with st.form("register_form"):
            col1, col2 = st.columns(2)

            with col1:
                reg_username = st.text_input(
                    "Username *",
                    placeholder="Choose a username",
                    help="Minimum 3 characters"
                )

                reg_email = st.text_input(
                    "Email *",
                    placeholder="your.email@example.com",
                    help="A valid email address"
                )

            with col2:
                reg_full_name = st.text_input(
                    "Full Name",
                    placeholder="Your full name (optional)"
                )

                reg_password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Choose a strong password",
                    help="Minimum 6 characters"
                )

            reg_password_confirm = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter your password"
            )

            st.markdown("*Required fields")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                register_button = st.form_submit_button("📝 Create Account", use_container_width=True)

            if register_button:
                # Validation
                errors = []

                if not reg_username or not reg_email or not reg_password or not reg_password_confirm:
                    errors.append("Please fill in all required fields")

                if len(reg_username) < 3:
                    errors.append("Username must be at least 3 characters")

                if len(reg_password) < 6:
                    errors.append("Password must be at least 6 characters")

                if reg_password != reg_password_confirm:
                    errors.append("Passwords do not match")

                if "@" not in reg_email or "." not in reg_email:
                    errors.append("Please enter a valid email address")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    with st.spinner("Creating account..."):
                        result = register_user(
                            email=reg_email,
                            username=reg_username,
                            password=reg_password,
                            full_name=reg_full_name if reg_full_name else None
                        )

                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            st.info("🔑 Please switch to the **Login** tab to sign in")
                        else:
                            st.error(f"❌ {result['error']}")

        st.divider()
        st.caption("Already have an account? Switch to the **Login** tab above")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🔒 Your data is secure and encrypted</p>
    <p>NLP Agentic AI Feedback Analysis System | Powered by FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)
