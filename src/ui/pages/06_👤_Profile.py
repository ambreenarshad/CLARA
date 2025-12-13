"""User Profile Management page."""

import streamlit as st
from datetime import datetime
from src.ui.utils.auth import (
    init_session_state,
    is_authenticated,
    require_authentication,
    update_profile,
    change_password,
    logout_user,
    get_auth_headers
)
import requests

# Page configuration
st.set_page_config(
    page_title="Profile - NLP Feedback Analysis",
    page_icon="👤",
    layout="wide"
)

# Initialize session state
init_session_state()

# Require authentication
require_authentication()

# Header
st.title("👤 User Profile")
st.markdown("Manage your account settings and preferences")

# Get user info
user_info = st.session_state.get("user_info", {})

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["📋 Account Information", "✏️ Edit Profile", "🔐 Change Password"])

# Tab 1: Account Information
with tab1:
    st.header("Account Information")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Details")

        info_data = {
            "Username": user_info.get('username', 'N/A'),
            "Email": user_info.get('email', 'N/A'),
            "Full Name": user_info.get('full_name', 'Not set'),
            "Account Status": "✅ Active" if user_info.get('is_active') else "❌ Inactive",
            "Email Verified": "✅ Yes" if user_info.get('is_verified') else "⏳ Pending"
        }

        for label, value in info_data.items():
            st.markdown(f"**{label}:** {value}")

    with col2:
        st.subheader("Account Statistics")

        # Fetch user statistics
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/statistics",
                headers=get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                stats = response.json().get("statistics", {})

                st.metric("Total Feedback Batches", stats.get("total_batches", 0))
                st.metric("Total Feedback Entries", stats.get("total_feedback", 0))
                st.metric("Total Analyses", stats.get("total_analyses", 0))
            else:
                st.warning("Could not load statistics")

        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")

    st.divider()

    # Account timestamps
    st.subheader("Account History")

    col1, col2 = st.columns(2)

    with col1:
        created_at = user_info.get('created_at')
        if created_at:
            st.markdown(f"**Account Created:** {created_at}")
        else:
            st.markdown("**Account Created:** N/A")

    with col2:
        updated_at = user_info.get('updated_at')
        if updated_at:
            st.markdown(f"**Last Updated:** {updated_at}")
        else:
            st.markdown("**Last Updated:** N/A")

# Tab 2: Edit Profile
with tab2:
    st.header("Edit Profile")
    st.markdown("Update your personal information")

    with st.form("edit_profile_form"):
        new_full_name = st.text_input(
            "Full Name",
            value=user_info.get('full_name', ''),
            placeholder="Enter your full name"
        )

        new_email = st.text_input(
            "Email",
            value=user_info.get('email', ''),
            placeholder="your.email@example.com",
            help="Changing email will require re-verification"
        )

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            submit_button = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if submit_button:
            # Check if anything changed
            changes = {}

            if new_full_name != user_info.get('full_name'):
                changes["full_name"] = new_full_name

            if new_email != user_info.get('email'):
                if "@" not in new_email or "." not in new_email:
                    st.error("❌ Please enter a valid email address")
                else:
                    changes["email"] = new_email

            if not changes:
                st.info("ℹ️ No changes detected")
            else:
                with st.spinner("Updating profile..."):
                    result = update_profile(
                        full_name=changes.get("full_name"),
                        email=changes.get("email")
                    )

                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        st.info("Refreshing page...")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

# Tab 3: Change Password
with tab3:
    st.header("Change Password")
    st.markdown("Update your account password")

    with st.form("change_password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter a new password",
            help="Minimum 6 characters"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            change_password_button = st.form_submit_button("🔑 Change Password", use_container_width=True)

        if change_password_button:
            # Validation
            errors = []

            if not current_password or not new_password or not confirm_password:
                errors.append("Please fill in all fields")

            if len(new_password) < 6:
                errors.append("New password must be at least 6 characters")

            if new_password != confirm_password:
                errors.append("New passwords do not match")

            if current_password == new_password:
                errors.append("New password must be different from current password")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                with st.spinner("Changing password..."):
                    result = change_password(current_password, new_password)

                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        st.info("Please login again with your new password")

                        # Logout after password change
                        logout_user()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

# Danger Zone
st.markdown("---")
st.header("⚠️ Danger Zone")

with st.expander("Account Actions"):
    st.warning("**Logout:** This will end your current session")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout_user()
            st.success("✅ Logged out successfully")
            st.info("Redirecting to login page...")
            st.rerun()

# Footer
st.markdown("---")
st.caption("💡 **Tip:** Keep your account information up to date for the best experience")
