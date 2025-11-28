import requests
import streamlit as st

def get_weather_forecast(city):
    api_key = st.secrets.get("openweather_Apikey") or st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key:
        return None, "Weather API key not configured"
    
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"]
            }
            
            return weather_info, None
        else:
            return None, f"City not found or API error: {response.status_code}"
    
    except Exception as e:
        return None, f"Error fetching weather: {str(e)}"

def get_forecast_5day(city):
    api_key = st.secrets.get("openweather_Apikey") or st.secrets.get("OPENWEATHER_API_KEY")
    
    if not api_key:
        return None, "Weather API key not configured"
    
    try:
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            forecast_list = []
            
            for item in data["list"][:8]:
                forecast_list.append({
                    "datetime": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"]
                })
            
            return forecast_list, None
        else:
            return None, f"City not found or API error: {response.status_code}"
    
    except Exception as e:
        return None, f"Error fetching forecast: {str(e)}"
