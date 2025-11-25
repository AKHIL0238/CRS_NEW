# Smart Crop Recommendation System

## Overview
This is an enhanced crop recommendation system built with Streamlit that helps farmers make informed decisions about which crops to cultivate based on soil and environmental parameters. The system uses machine learning models and integrates modern features including AI chatbot, weather forecasting, community forums, and multilingual support.

## Recent Changes (November 25, 2025)
- ✅ Migrated from GitHub import to Replit environment
- ✅ Added Firebase authentication (demo mode enabled, real auth optional via env vars)
- ✅ Added Telugu language support for regional users
- ✅ Integrated weather forecast using OpenWeather API
- ✅ **Migrated forum to Firebase Firestore for reliable data persistence**
- ✅ **Added search functionality to forum discussions**
- ✅ **Implemented reply functionality for forum posts**
- ✅ **Enhanced forum UI with reply display and nested comments**
- ✅ Enhanced UI with modern design and navigation
- ✅ Integrated AI chatbot using Hugging Face Mistral model
- ✅ Configured Streamlit to run on port 5000 with proxy support
- ✅ Secured all API keys using environment variables (no hardcoded secrets)
- ✅ Set up modular code structure with utilities
- ✅ Added comprehensive error handling and input sanitization

## Project Architecture

### File Structure
```
├── app_enhanced.py          # Main Streamlit application (ACTIVE)
├── st_app.py                # Original simple app (legacy)
├── app.py                   # Flask app (legacy)
├── model.pkl                # Trained ML model
├── standscaler.pkl          # Standard scaler for features
├── minmaxscaler.pkl         # MinMax scaler for features
├── utils/
│   ├── translations.py      # English & Telugu translations
│   ├── firebase_auth.py     # Authentication module
│   ├── weather.py           # Weather API integration
│   └── forum.py             # Community forum logic
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── forum_data.json          # Forum posts storage (auto-generated)
```

### Key Features
1. **Crop Recommendation**: ML-based prediction using soil parameters (N, P, K, pH, temperature, humidity, rainfall)
2. **AI Chatbot**: Context-aware agricultural assistant using Hugging Face Mistral model
3. **Weather Forecast**: Real-time weather data and 24-hour forecast
4. **Community Forums**: 
   - Post discussions and share farming knowledge
   - Search through all posts and replies
   - Reply to posts with threaded conversations
   - Firebase Firestore backend with JSON fallback
   - Persistent storage for all conversations
5. **Multilingual**: English and Telugu language support
6. **User Authentication**: Firebase-based login/signup (demo mode active)

### Technology Stack
- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.11
- **ML**: scikit-learn (Random Forest model)
- **APIs**: 
  - Hugging Face Inference API (Mistral-Nemo)
  - OpenWeather API
- **Auth**: Firebase (Pyrebase4)
- **Storage**: Firebase Firestore for forum data (with JSON fallback)

## Environment Variables
The following secrets are configured:
- `FIREBASE_APIKEY`: Firebase API key for authentication
- `firebase_authdomain`: Firebase auth domain
- `firebase_projectid`: Firebase project ID
- `openweather_Apikey`: API key for weather forecasts
- `FIREBASE_SERVICE_ACCOUNT_KEY`: (Optional) Firebase service account JSON for Firestore forum storage
- `HUGGINGFACE_API_TOKEN`: (Optional) API key for Hugging Face chatbot

## User Preferences
- Preserve all existing ML models (model.pkl, standscaler.pkl, minmaxscaler.pkl)
- Keep enhanced UI with modern design
- Maintain Firebase authentication
- Keep multilingual support (Telugu + English)
- Preserve community forums feature
- Keep weather forecast integration
- Keep AI chatbot functionality

## Running the Application
The app runs on port 5000 with the command:
```
streamlit run app_enhanced.py
```

## Firebase Configuration
Currently using demo mode (any email/password works locally). To enable real Firebase authentication:
1. Create a Firebase project at https://firebase.google.com
2. Enable Email/Password authentication in Firebase Console
3. Add the following to Replit Secrets:
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
4. App automatically switches from demo mode to real authentication

See SETUP.md for detailed instructions.

## Deployment Notes
- Configured for Streamlit on port 5000
- CORS and XSRF disabled for Replit iframe compatibility
- Server address set to 0.0.0.0 for proxy support
