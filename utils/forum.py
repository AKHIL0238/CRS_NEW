import json
import os
from datetime import datetime
import re
import streamlit as st


db = None
FIRESTORE_ERROR = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    service_account_json = st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]
    
    if service_account_json:
        try:
            service_account_dict = json.loads(service_account_json)
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(service_account_dict)
                firebase_admin.initialize_app(cred)
            
            db = firestore.client()
            print("Firestore initialized successfully for forum")
        except Exception as e:
            FIRESTORE_ERROR = f"Firestore initialization failed: {e}"
            print(f"Firestore initialization failed: {e}")
    else:
        FIRESTORE_ERROR = "FIREBASE_SERVICE_ACCOUNT_KEY secret is not configured"
        print("FIREBASE_SERVICE_ACCOUNT_KEY not found")
except ImportError as e:
    FIRESTORE_ERROR = f"firebase-admin package not available: {e}"
    print(f"firebase-admin not available: {e}")

def is_firestore_configured():
    return db is not None

def get_firestore_error():
    return FIRESTORE_ERROR

def sanitize_input(text, max_length=500):
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()[:max_length]
    text = re.sub(r'<[^>]+>', '', text)
    return text

def add_forum_post(name, topic, message):
    if not db:
        return False, "Firebase Firestore is not configured"
    
    name = sanitize_input(name, 100)
    topic = sanitize_input(topic, 200)
    message = sanitize_input(message, 1000)
    
    if not name or not topic or not message:
        return False, "All fields are required"
    
    if len(name) < 2 or len(topic) < 5 or len(message) < 10:
        return False, "Input too short"
    
    try:
        post_data = {
            "name": name,
            "topic": topic,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "created_at": datetime.now().isoformat(),
            "reply_count": 0
        }
        db.collection('forum_posts').add(post_data)
        return True, "Post added successfully"
    except Exception as e:
        print(f"Error adding post to Firestore: {e}")
        return False, f"Error: {e}"

def get_forum_posts(limit=10):
    if not db:
        return []
    
    try:
        posts_ref = db.collection('forum_posts').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        posts = []
        
        for doc in posts_ref.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            
            if 'timestamp' in post_data and post_data['timestamp']:
                post_data['timestamp'] = post_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            elif 'created_at' in post_data:
                post_data['timestamp'] = post_data['created_at'][:19].replace('T', ' ')
            else:
                post_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            replies_ref = db.collection('forum_posts').document(doc.id).collection('replies').order_by('timestamp')
            replies = []
            for reply_doc in replies_ref.stream():
                reply_data = reply_doc.to_dict()
                if 'timestamp' in reply_data and reply_data['timestamp']:
                    reply_data['timestamp'] = reply_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                elif 'created_at' in reply_data:
                    reply_data['timestamp'] = reply_data['created_at'][:19].replace('T', ' ')
                replies.append(reply_data)
            
            post_data['replies'] = replies
            posts.append(post_data)
        
        return posts
    except Exception as e:
        print(f"Error getting posts from Firestore: {e}")
        return []

def add_reply(post_id, name, message):
    if not db:
        return False, "Firebase Firestore is not configured"
    
    name = sanitize_input(name, 100)
    message = sanitize_input(message, 1000)
    
    if not name or not message:
        return False, "All fields are required"
    
    if len(name) < 2 or len(message) < 5:
        return False, "Input too short"
    
    try:
        reply_data = {
            "name": name,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "created_at": datetime.now().isoformat()
        }
        
        post_ref = db.collection('forum_posts').document(post_id)
        post_ref.collection('replies').add(reply_data)
        
        post_ref.update({
            "reply_count": firestore.Increment(1)
        })
        
        return True, "Reply added successfully"
    except Exception as e:
        print(f"Error adding reply to Firestore: {e}")
        return False, f"Error: {e}"

def search_forum_posts(query):
    if not db:
        return []
    
    if not query or len(query) < 2:
        return []
    
    query_lower = query.lower()
    
    try:
        all_posts = get_forum_posts(limit=1000)
        results = []
        
        for post in all_posts:
            post_text = f"{post.get('topic', '')} {post.get('message', '')} {post.get('name', '')}".lower()
            
            reply_text = ""
            for reply in post.get("replies", []):
                reply_text += f" {reply.get('message', '')} {reply.get('name', '')}".lower()
            
            combined_text = post_text + reply_text
            
            if query_lower in combined_text:
                results.append(post)
        
        return results
    except Exception as e:
        print(f"Error searching Firestore: {e}")
        return []
