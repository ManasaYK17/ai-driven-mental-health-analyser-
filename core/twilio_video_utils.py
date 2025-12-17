import os
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

# Load Twilio credentials from environment variables or settings
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_API_KEY_SID = os.getenv('TWILIO_API_KEY_SID')
TWILIO_API_KEY_SECRET = os.getenv('TWILIO_API_KEY_SECRET')

client = Client(TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, TWILIO_ACCOUNT_SID)

def create_video_room(room_name):
    """
    Create a Twilio Video Room with the given name.
    """
    try:
        room = client.video.rooms.create(
            unique_name=room_name,
            type='group',  # or 'peer-to-peer' depending on use case
            record_participants_on_connect=False
        )
        return room.sid, None
    except Exception as e:
        return None, str(e)

def generate_access_token(identity, room_name):
    """
    Generate an access token for a user to join a Twilio Video Room.
    """
    token = AccessToken(TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, identity=identity)
    video_grant = VideoGrant(room=room_name)
    token.add_grant(video_grant)
    return token.to_jwt().decode('utf-8')
