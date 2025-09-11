# Utility for creating Zoom meetings using Zoom API
import requests
from django.conf import settings
import jwt
import datetime

def create_zoom_meeting(topic, start_time, duration=30):
    api_key = getattr(settings, 'ZOOM_API_KEY', None)
    api_secret = getattr(settings, 'ZOOM_API_SECRET', None)
    user_id = getattr(settings, 'ZOOM_USER_ID', None)
    if not all([api_key, api_secret, user_id]):
        return None, 'Zoom credentials not set.'
    payload = {
        'iss': api_key,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    token = jwt.encode(payload, api_secret, algorithm='HS256')
    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }
    url = f'https://api.zoom.us/v2/users/{user_id}/meetings'
    data = {
        'topic': topic,
        'type': 2,
        'start_time': start_time.isoformat(),
        'duration': duration,
        'timezone': 'UTC',
        'settings': {
            'join_before_host': True,
            'waiting_room': False
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()['join_url'], None
    else:
        return None, response.text
