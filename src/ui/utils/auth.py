"""Authentication utilities for Streamlit UI."""

import streamlit as st
import requests
from typing import Optional, Dict
from datetime import datetime, timedelta

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"


def init_session_state():
    """Initialize authentication session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "token_expiry" not in st.session_state:
        st.session_state.token_expiry = None


def register_user(email: str, username: str, password: str, full_name: Optional[str] = None) -> Dict:
    """
    Register a new user.

    Args:
        email: User email
        username: Username
        password: Password
        full_name: Optional full name

    Returns:
        Dict with success status and message or error
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name
            },
            timeout=10
        )

        if response.status_code == 201:
            return {
                "success": True,
                "message": "Registration successful! Please login.",
                "user": response.json()
            }
        else:
            error_detail = response.json().get("detail", "Registration failed")
            return {
                "success": False,
                "error": error_detail
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Could not connect to API server. Please ensure the server is running."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


def login_user(username: str, password: str) -> Dict:
    """
    Login a user and store the access token.

    Args:
        username: Username or email
        password: Password

    Returns:
        Dict with success status and message or error
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()

            # Store authentication data in session state
            st.session_state.authenticated = True
            st.session_state.access_token = token_data["access_token"]
            st.session_state.token_expiry = datetime.now() + timedelta(
                minutes=token_data.get("expires_in", 30)
            )

            # Fetch user info
            user_info = get_current_user()
            if user_info:
                st.session_state.user_info = user_info

            return {
                "success": True,
                "message": f"Welcome back, {token_data.get('username', 'User')}!",
                "token": token_data["access_token"]
            }
        else:
            error_detail = response.json().get("detail", "Login failed")
            return {
                "success": False,
                "error": error_detail
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Could not connect to API server. Please ensure the server is running."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


def logout_user():
    """Logout the current user and clear session state."""
    try:
        if st.session_state.get("access_token"):
            # Call logout endpoint
            requests.post(
                f"{API_BASE_URL}/auth/logout",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                timeout=5
            )
    except:
        pass  # Ignore errors during logout API call

    # Clear session state
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.token_expiry = None


def get_current_user() -> Optional[Dict]:
    """
    Get current authenticated user information.

    Returns:
        User info dict or None if not authenticated
    """
    if not st.session_state.get("access_token"):
        return None

    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Token might be invalid, logout
            logout_user()
            return None

    except:
        return None


def is_authenticated() -> bool:
    """
    Check if user is authenticated and token is still valid.

    Returns:
        True if authenticated, False otherwise
    """
    if not st.session_state.get("authenticated"):
        return False

    if not st.session_state.get("access_token"):
        return False

    # Check token expiry
    if st.session_state.get("token_expiry"):
        if datetime.now() >= st.session_state.token_expiry:
            logout_user()
            return False

    return True


def get_auth_headers() -> Dict[str, str]:
    """
    Get authorization headers for API requests.

    Returns:
        Headers dict with Bearer token
    """
    if not st.session_state.get("access_token"):
        return {}

    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def require_authentication():
    """
    Decorator/function to require authentication for a page.
    Redirects to login if not authenticated.
    """
    if not is_authenticated():
        st.warning("⚠️ Please login to access this page")
        st.info("👉 Navigate to the **Login** page from the sidebar")
        st.stop()


def update_profile(full_name: Optional[str] = None, email: Optional[str] = None) -> Dict:
    """
    Update user profile.

    Args:
        full_name: New full name
        email: New email

    Returns:
        Dict with success status and message or error
    """
    if not is_authenticated():
        return {"success": False, "error": "Not authenticated"}

    try:
        data = {}
        if full_name is not None:
            data["full_name"] = full_name
        if email is not None:
            data["email"] = email

        if not data:
            return {"success": False, "error": "No updates provided"}

        response = requests.put(
            f"{API_BASE_URL}/auth/me",
            json=data,
            headers=get_auth_headers(),
            timeout=10
        )

        if response.status_code == 200:
            # Update user info in session state
            st.session_state.user_info = response.json()
            return {
                "success": True,
                "message": "Profile updated successfully!",
                "user": response.json()
            }
        else:
            error_detail = response.json().get("detail", "Update failed")
            return {
                "success": False,
                "error": error_detail
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


def change_password(current_password: str, new_password: str) -> Dict:
    """
    Change user password.

    Args:
        current_password: Current password
        new_password: New password

    Returns:
        Dict with success status and message or error
    """
    if not is_authenticated():
        return {"success": False, "error": "Not authenticated"}

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/change-password",
            json={
                "current_password": current_password,
                "new_password": new_password
            },
            headers=get_auth_headers(),
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Password changed successfully!"
            }
        else:
            error_detail = response.json().get("detail", "Password change failed")
            return {
                "success": False,
                "error": error_detail
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }
