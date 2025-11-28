import streamlit as st
import os
import pyrebase

# 1. Load Secrets safely
# We try to get them from st.secrets first, then os.getenv
firebase_api_key = st.secrets.get("FIREBASE_API_KEY") or os.getenv("FIREBASE_API_KEY")
firebase_auth_domain = st.secrets.get("FIREBASE_AUTH_DOMAIN") or os.getenv("FIREBASE_AUTH_DOMAIN")
firebase_project_id = st.secrets.get("FIREBASE_PROJECT_ID") or os.getenv("FIREBASE_PROJECT_ID")

# 2. Initialize Firebase conditionally
auth = None
firebase = None

if firebase_api_key and firebase_auth_domain and firebase_project_id:
    try:
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
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
else:
    st.warning("Firebase credentials not found. Running in DEMO MODE (Fake Auth).")

# 3. Session State Management
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

# 4. Authentication Functions
def login_user(email, password):
    if not email or not password:
        return False, "Please enter both email and password"

    # Handle Demo/Offline Mode
    if auth is None:
        st.session_state.user = {"localId": "demo_user", "email": email}
        st.session_state.user_email = email
        return True, "✅ Login successful! (Demo Mode)"

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        st.session_state.user_email = email
        return True, "✅ Login successful!"
    except Exception as e:
        error_msg = str(e)
        # Parse Pyrebase JSON error response
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
    
    # Handle Demo/Offline Mode
    if auth is None:
        st.session_state.user = {"localId": "demo_user", "email": email}
        st.session_state.user_email = email
        return True, "✅ Account created (Demo mode - Firebase not configured)"
    
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
    st.rerun() # Immediately refresh the app to show login screen

def is_logged_in():
    return st.session_state.user is not None

# --- UI IMPLEMENTATION FOR TESTING ---
def main():
    st.title("Firebase Auth Starter")
    init_session_state()

    if is_logged_in():
        st.success(f"Welcome back, {st.session_state.user_email}!")
        if st.button("Logout"):
            logout_user()
    else:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In"):
                success, msg = login_user(email, password)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with tab2:
            st.subheader("Sign Up")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Create Account"):
                success, msg = signup_user(new_email, new_password)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

if __name__ == "__main__":
    main()
