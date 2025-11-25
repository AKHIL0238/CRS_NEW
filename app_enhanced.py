import streamlit as st
import numpy as np
import pickle
import os
from utils.translations import get_text
from utils.firebase_auth import init_session_state, login_user, signup_user, logout_user, is_logged_in
from utils.weather import get_weather_forecast, get_forecast_5day
from utils.forum import add_forum_post, get_forum_posts, add_reply, search_forum_posts
import requests

st.set_page_config(
    page_title="Smart Crop Recommendation System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .forum-post {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
        color: black;
    }
    .crop-result {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        font-size: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
    8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
    14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
    19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

@st.cache_resource
def load_models():
    try:
        model = pickle.load(open('model.pkl', 'rb'))
        sc = pickle.load(open('standscaler.pkl', 'rb'))
        ms = pickle.load(open('minmaxscaler.pkl', 'rb'))
        return model, sc, ms
    except FileNotFoundError as e:
        st.error(f"Error loading model files: {str(e)}")
        return None, None, None

def predict_crop(features, model, sc, ms):
    try:
        single_pred = np.array(features).reshape(1, -1)
        scaled_features = ms.transform(single_pred)
        final_features = sc.transform(scaled_features)
        prediction = model.predict(final_features)
        
        if prediction[0] in crop_dict:
            return crop_dict[prediction[0]]
        return None
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")
        return None

def ai_recommendations(crop, features, chat_input=None, chat_history=None, lang="en"):
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    
    if not api_token:
        return "AI chatbot not configured. Please add HUGGINGFACE_API_TOKEN."
    
    language_instruction = ""
    if lang == "te":
        language_instruction = "Please provide the response in Telugu language."
    
    base_prompt = f"""Provide detailed agricultural guidance for {crop} cultivation, 
    focusing on:
    1. Optimal cultivation process
    2. Recommended fertilizers
    3. Pest prevention strategies
    4. Best cultivation seasons
    5. Key growth requirements
    
    {language_instruction}"""

    detailed_prompt = f"""{base_prompt}

    Detailed Soil and Environmental Parameters:
    - Nitrogen: {features[0]:.1f}
    - Phosphorus: {features[1]:.1f}
    - Potassium: {features[2]:.1f}
    - Temperature: {features[3]:.1f}°C
    - Humidity: {features[4]:.1f}%
    - pH: {features[5]:.1f}
    - Rainfall: {features[6]:.1f} mm

    Provide comprehensive agricultural insights taking these specific parameters into account."""

    if chat_input:
        detailed_prompt += f"\n\nLatest User Query: {chat_input}"

    headers = {"Authorization": f"Bearer {api_token}"}
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": detailed_prompt}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "Unable to fetch agricultural insights.")
            return "Unable to fetch agricultural insights."
        else:
            return f"Unable to fetch agricultural insights. Status: {response.status_code}"
    except Exception as e:
        return f"Error fetching insights: {str(e)}"

def show_login_page(lang):
    st.markdown(f"<h1 class='main-header'>{get_text(lang, 'app_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{get_text(lang, 'welcome')}</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([get_text(lang, 'login'), get_text(lang, 'signup')])
    
    with tab1:
        st.subheader(get_text(lang, 'login'))
        email = st.text_input(get_text(lang, 'email'), key="login_email")
        password = st.text_input(get_text(lang, 'password'), type="password", key="login_password")
        
        if st.button(get_text(lang, 'login'), key="login_btn"):
            if email and password:
                success, message = login_user(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both email and password")
    
    with tab2:
        st.subheader(get_text(lang, 'signup'))
        email = st.text_input(get_text(lang, 'email'), key="signup_email")
        password = st.text_input(get_text(lang, 'password'), type="password", key="signup_password")
        
        if st.button(get_text(lang, 'signup'), key="signup_btn"):
            if email and password:
                success, message = signup_user(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both email and password")

def show_home_page(lang, model, sc, ms):
    st.markdown(f"<h2>🌾 {get_text(lang, 'recommended_crop')}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        nitrogen = st.number_input(get_text(lang, 'nitrogen'), min_value=0.0, max_value=140.0, step=1.0, value=90.0)
        phosphorus = st.number_input(get_text(lang, 'phosphorus'), min_value=0.0, max_value=145.0, step=1.0, value=42.0)
        potassium = st.number_input(get_text(lang, 'potassium'), min_value=0.0, max_value=205.0, step=1.0, value=43.0)
        temperature = st.number_input(get_text(lang, 'temperature'), min_value=0.0, max_value=50.0, step=0.1, value=20.8)

    with col2:
        humidity = st.number_input(get_text(lang, 'humidity'), min_value=0.0, max_value=100.0, step=0.1, value=82.0)
        ph = st.number_input(get_text(lang, 'ph'), min_value=0.0, max_value=14.0, step=0.1, value=6.5)
        rainfall = st.number_input(get_text(lang, 'rainfall'), min_value=0.0, max_value=300.0, step=0.1, value=202.9)

    if st.button(get_text(lang, 'get_recommendation'), type="primary"):
        feature_list = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        result = predict_crop(feature_list, model, sc, ms)
        if result:
            st.session_state.chat_history = []
            st.session_state.current_crop = result
            st.session_state.current_features = feature_list
            
            st.markdown(f"""<div class='crop-result'>
                🌱 {result}
            </div>""", unsafe_allow_html=True)
            
            with st.spinner("Generating Agricultural insights..."):
                description = ai_recommendations(result, feature_list, lang=lang)
            with st.expander(f"📚 {get_text(lang, 'crop_insights')} - {result}", expanded=True):
                st.write(description)
    
    if st.session_state.get('current_crop'):
        st.divider()
        st.subheader(f"🤖 {get_text(lang, 'ai_chat')} - {st.session_state.current_crop}")
        
        for msg in st.session_state.get('chat_history', []):
            st.chat_message(msg['role']).write(msg['content'])
        
        chat_input = st.chat_input(get_text(lang, 'ask_question'))
        if chat_input:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': chat_input
            })
            st.chat_message('user').write(chat_input)
            
            with st.spinner("Generating response..."):
                chat_response = ai_recommendations(
                    st.session_state.current_crop, 
                    st.session_state.current_features, 
                    chat_input, 
                    st.session_state.chat_history,
                    lang=lang
                )
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': chat_response
                })
                st.chat_message('assistant').write(chat_response)

def show_weather_page(lang):
    st.markdown(f"<h2>🌤️ {get_text(lang, 'weather')}</h2>", unsafe_allow_html=True)
    
    city = st.text_input(get_text(lang, 'weather_location'), value="Hyderabad")
    
    if st.button(get_text(lang, 'get_weather'), type="primary"):
        weather_info, error = get_weather_forecast(city)
        
        if weather_info:
            st.markdown(f"""
            <div class='weather-card'>
                <h2>📍 {weather_info['city']}, {weather_info['country']}</h2>
                <h1>🌡️ {weather_info['temperature']:.1f}°C</h1>
                <p style='font-size: 1.2rem;'>Feels like: {weather_info['feels_like']:.1f}°C</p>
                <p style='font-size: 1.2rem;'>💧 Humidity: {weather_info['humidity']}%</p>
                <p style='font-size: 1.2rem;'>🌬️ Wind Speed: {weather_info['wind_speed']} m/s</p>
                <p style='font-size: 1.2rem;'>📊 Pressure: {weather_info['pressure']} hPa</p>
                <p style='font-size: 1.5rem; text-transform: capitalize;'>{weather_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            forecast, error = get_forecast_5day(city)
            if forecast:
                st.subheader("📅 24-Hour Forecast")
                cols = st.columns(4)
                for i, item in enumerate(forecast[:4]):
                    with cols[i]:
                        st.metric(
                            label=item['datetime'].split()[1][:5],
                            value=f"{item['temp']:.1f}°C",
                            delta=f"{item['humidity']}% humidity"
                        )
                        st.caption(item['description'].capitalize())
        else:
            st.error(error)

def show_forum_page(lang):
    st.markdown(f"<h2>💬 {get_text(lang, 'forum_title')}</h2>", unsafe_allow_html=True)
    st.write(get_text(lang, 'forum_desc'))
    
    with st.expander("✍️ Post a New Discussion", expanded=False):
        name = st.text_input(get_text(lang, 'your_name'), max_chars=100, key="new_post_name")
        topic = st.text_input(get_text(lang, 'discussion_topic'), max_chars=200, key="new_post_topic")
        message = st.text_area(get_text(lang, 'your_message'), max_chars=1000, key="new_post_message")
        
        if st.button(get_text(lang, 'post_message'), type="primary", key="submit_post"):
            if name and topic and message:
                if len(name) < 2:
                    st.warning("Name must be at least 2 characters")
                elif len(topic) < 5:
                    st.warning("Topic must be at least 5 characters")
                elif len(message) < 10:
                    st.warning("Message must be at least 10 characters")
                else:
                    success = add_forum_post(name, topic, message)
                    if success:
                        st.success("✅ Your post has been added!")
                        st.rerun()
                    else:
                        st.error("Failed to add post. Please try again.")
            else:
                st.warning("Please fill in all fields")
    
    st.markdown("---")
    
    search_query = st.text_input("🔍 Search discussions...", placeholder="Search by topic, message, or name", key="forum_search")
    
    if search_query and len(search_query) >= 2:
        st.subheader(f"🔎 Search Results for: '{search_query}'")
        posts = search_forum_posts(search_query)
        if not posts:
            st.info("No discussions found matching your search.")
    else:
        st.subheader(f"📋 {get_text(lang, 'recent_discussions')}")
        posts = get_forum_posts(15)
    
    if posts:
        for idx, post in enumerate(posts):
            post_id = post.get('id', idx)
            
            st.markdown(f"""
            <div class='forum-post'>
                <h4>📌 {post['topic']}</h4>
                <p><strong>👤 {post['name']}</strong> • <em>{post['timestamp']}</em></p>
                <p>{post['message']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            replies = post.get('replies', [])
            if replies:
                st.markdown(f"**💬 {len(replies)} Replies:**")
                for reply_idx, reply in enumerate(replies):
                    st.markdown(f"""
                    <div style='margin-left: 2rem; padding: 0.8rem; background-color: #e8f5e9; border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid #4CAF50;'>
                        <p style='margin: 0; color: black;'><strong>👤 {reply['name']}</strong> • <em>{reply['timestamp']}</em></p>
                        <p style='margin: 0.3rem 0 0 0; color: black;'>{reply['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with st.expander(f"💬 Reply to this post"):
                reply_name = st.text_input("Your name", max_chars=100, key=f"reply_name_{post_id}")
                reply_message = st.text_area("Your reply", max_chars=1000, key=f"reply_message_{post_id}")
                
                if st.button("Post Reply", type="secondary", key=f"submit_reply_{post_id}"):
                    if reply_name and reply_message:
                        if len(reply_name) < 2:
                            st.warning("Name must be at least 2 characters")
                        elif len(reply_message) < 5:
                            st.warning("Reply must be at least 5 characters")
                        else:
                            success = add_reply(post_id, reply_name, reply_message)
                            if success:
                                st.success("✅ Reply added!")
                                st.rerun()
                            else:
                                st.error("Failed to add reply. Please try again.")
                    else:
                        st.warning("Please fill in both fields")
            
            st.markdown("---")
    else:
        st.info("No discussions yet. Be the first to post!")

def main():
    init_session_state()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_crop' not in st.session_state:
        st.session_state.current_crop = None
    if 'current_features' not in st.session_state:
        st.session_state.current_features = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=100)
        st.title("🌱 Menu")
        
        lang = st.selectbox(
            "🌐 Language / భాష",
            options=['en', 'te'],
            format_func=lambda x: "English" if x == 'en' else "తెలుగు",
            index=0 if st.session_state.language == 'en' else 1
        )
        st.session_state.language = lang
        
        if is_logged_in():
            st.success(f"✅ Logged in as: {st.session_state.user_email}")
            
            page = st.radio(
                "Navigation",
                [get_text(lang, 'home'), get_text(lang, 'weather'), 
                 get_text(lang, 'forums'), get_text(lang, 'ai_chat')],
                label_visibility="collapsed"
            )
            
            if st.button(get_text(lang, 'logout')):
                logout_user()
                st.rerun()
        else:
            page = "Login"
    
    if not is_logged_in():
        show_login_page(lang)
    else:
        model, sc, ms = load_models()
        
        if model is None:
            st.error("Failed to load ML models. Please check model files.")
            return
        
        if page == get_text(lang, 'home'):
            show_home_page(lang, model, sc, ms)
        elif page == get_text(lang, 'weather'):
            show_weather_page(lang)
        elif page == get_text(lang, 'forums'):
            show_forum_page(lang)
        elif page == get_text(lang, 'ai_chat'):
            st.info("Please get a crop recommendation first from the Home page to start chatting!")

if __name__ == "__main__":
    main()
