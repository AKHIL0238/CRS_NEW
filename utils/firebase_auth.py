import streamlit as st
import requests
import os

FIREBASE_API_KEY = st.secrets.get("FIREBASE_APIKEY") or os.getenv("FIREBASE_APIKEY")

# 2. Session Management
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

def is_logged_in():
    return st.session_state.user is not None

def logout_user():
    st.session_state.user = None
    st.session_state.user_email = None
    st.rerun()

# 3. Native Authentication Functions (No Pyrebase required)
def _firebase_auth_request(endpoint, email, password):
    """Internal helper to send requests to Firebase REST API"""
    if not FIREBASE_API_KEY:
        # Fallback for Demo Mode if secrets are missing
        return {"localId": "demo_user", "email": email, "idToken": "demo_token"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    
    # Handle Errors
    if not response.ok:
        try:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown Error')
        except:
            error_msg = response.text
        raise Exception(error_msg)
        
    return response.json()

def login_user(email, password):
    if not email or not password:
        return False, "Please enter both email and password"

    try:
        # Use the signInWithPassword endpoint
        user_data = _firebase_auth_request("signInWithPassword", email, password)
        
        # Success
        st.session_state.user = user_data
        st.session_state.user_email = email
        return True, "✅ Login successful!"
        
    except Exception as e:
        error_msg = str(e)
        if "INVALID_PASSWORD" in error_msg or "INVALID_EMAIL" in error_msg:
            return False, "Invalid email or password"
        elif "EMAIL_NOT_FOUND" in error_msg:
            return False, "No account found with this email"
        elif "USER_DISABLED" in error_msg:
            return False, "This account has been disabled"
        return False, f"Login failed: {error_msg}"

def signup_user(email, password):
    if not email or not password:
        return False, "Please enter both email and password"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    try:
        # Use the signUp endpoint
        user_data = _firebase_auth_request("signUp", email, password)
        
        # Success
        st.session_state.user = user_data
        st.session_state.user_email = email
        return True, "✅ Account created successfully!"
        
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, "An account with this email already exists"
        elif "WEAK_PASSWORD" in error_msg:
            return False, "Password is too weak"
        return False, f"Signup failed: {error_msg}"
