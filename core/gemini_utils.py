import os
import requests
from django.conf import settings

def get_gemini_response(prompt, role='assistant'):
    api_key = os.getenv('GEMINI_API_KEY', getattr(settings, 'GEMINI_API_KEY', None))
    if not api_key:
        return "Gemini API key not set."
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": f"You are a helpful {role} for student mental health. {prompt}"}]
        }]
    }
    params = {"key": api_key}
    try:
        response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Gemini error: {e}"
