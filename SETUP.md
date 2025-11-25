# Setup Instructions

## Required Environment Variables

This application uses the following secrets that must be configured in Replit Secrets:

### 1. **HUGGINGFACE_API_TOKEN** (Required for AI Chatbot)
Get your API token from https://huggingface.co/settings/tokens

**Steps:**
1. Create a free Hugging Face account
2. Go to Settings → Access Tokens
3. Create a new token with "Read" access
4. Add it to Replit Secrets as `HUGGINGFACE_API_TOKEN`

### 2. **OPENWEATHER_API_KEY** (Required for Weather Forecast)
Get your API key from https://openweathermap.org/api

**Steps:**
1. Create a free OpenWeather account
2. Go to API Keys section
3. Generate a new API key
4. Add it to Replit Secrets as `OPENWEATHER_API_KEY`

### 3. **Firebase Authentication** (Optional - Demo Mode Available)

The app works in demo mode without Firebase. To enable real authentication:

**Required Secrets:**
- `FIREBASE_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`

**Optional:**
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`

**Steps to enable Firebase:**
1. Go to https://firebase.google.com
2. Create a new Firebase project
3. Enable Email/Password authentication in Authentication → Sign-in method
4. Get your config from Project Settings → General → Your apps
5. Add the credentials to Replit Secrets

**Note:** Without Firebase secrets, the app runs in demo mode where any email/password combination will work locally. This is fine for testing but not for production.

## Features Status

✅ **Crop Recommendation** - ML-based prediction (works immediately)
✅ **AI Chatbot** - Requires HUGGINGFACE_API_TOKEN
✅ **Weather Forecast** - Requires OPENWEATHER_API_KEY
✅ **Community Forums** - Works immediately (file-based storage)
✅ **User Authentication** - Demo mode (Firebase optional)
✅ **Telugu Language Support** - Works immediately

## Running the Application

The app automatically runs on port 5000 using:
```bash
streamlit run app_enhanced.py
```

## Security Notes

- ✅ All API keys are stored as environment variables
- ✅ Forum posts are validated and sanitized
- ✅ Input length limits enforced
- ✅ No hardcoded credentials in code
- ⚠️ Forum data is stored in `forum_data.json` (ephemeral in Replit)
- ⚠️ Demo mode allows any login (for testing only)

## Troubleshooting

**"AI chatbot not configured"**
→ Add HUGGINGFACE_API_TOKEN to Replit Secrets

**"Weather API key not configured"**
→ Add OPENWEATHER_API_KEY to Replit Secrets

**Authentication always in demo mode**
→ This is normal if Firebase secrets are not configured. Add Firebase credentials to enable real auth.

**Forum posts disappear**
→ Forum data is stored in a JSON file which is ephemeral in Replit. For production, consider using a database.
