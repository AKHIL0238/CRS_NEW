import streamlit as st
import os
DEMO_MODE = True

try:
    import pyrebase
    firebase_api_key = st.secrets.get("FIREBASE_APIKEY") or os.getenv("FIREBASE_API_KEY")
    firebase_auth_domain = st.secrets.get("firebase_authdomain") or st.secrets.get("FIREBASE_AUTH_DOMAIN")
    firebase_project_id = st.secrets.get("firebase_projectid") or st.secrets.get("FIREBASE_PROJECT_ID")
    
    if firebase_api_key and firebase_auth_domain and firebase_project_id:
        firebase_config = {
            "apiKey": firebase_api_key,
            "authDomain": firebase_auth_domain,
            "databaseURL": f"https://{firebase_project_id}.firebaseio.com",
            "projectId": firebase_project_id,
            "storageBucket": f"{firebase_project_id}.appspot.com",
            "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": st.secrets.get("FIREBASE_APP_ID", "")
        }
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        DEMO_MODE = False
    else:
        auth = None
        DEMO_MODE = True
except Exception as e:
    auth = None
    DEMO_MODE = True
    print(f"Firebase initialization error (using demo mode): {e}")

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

def login_user(email, password):
    if not email or not password:
        return False, "Please enter both email and password"
    
    if DEMO_MODE or auth is None:
        st.session_state.user = {"localId": "demo_user"}
        st.session_state.user_email = email
        return True, "✅ Logged in (Demo mode - Firebase not configured. To enable real auth, add Firebase credentials)"
    
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        st.session_state.user_email = email
        return True, "✅ Login successful!"
    except Exception as e:
        error_msg = str(e)
        if "INVALID_PASSWORD" in error_msg or "INVALID_EMAIL" in error_msg:
            return False, "Invalid email or password"
        elif "EMAIL_NOT_FOUND" in error_msg:
            return False, "No account found with this email"
        return False, f"Login failed: {error_msg}"

def signup_user(email, password):
    if not email or not password:
        return False, "Please enter both email and password"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if DEMO_MODE or auth is None:
        st.session_state.user = {"localId": "demo_user"}
        st.session_state.user_email = email
        return True, "✅ Account created (Demo mode - Firebase not configured. To enable real auth, add Firebase credentials)"
    
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.session_state.user = user
        st.session_state.user_email = email
        return True, "✅ Account created successfully!"
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, "An account with this email already exists"
        elif "INVALID_EMAIL" in error_msg:
            return False, "Please enter a valid email address"
        elif "WEAK_PASSWORD" in error_msg:
            return False, "Password is too weak. Use at least 6 characters"
        return False, f"Signup failed: {error_msg}"

def logout_user():
    st.session_state.user = None
    st.session_state.user_email = None

def is_logged_in():
    return st.session_state.user is not None
