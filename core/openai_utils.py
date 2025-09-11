import os
import openai
from django.conf import settings

def get_openai_response(prompt, role='assistant'):
    api_key = os.getenv('OPENAI_API_KEY', getattr(settings, 'OPENAI_API_KEY', None))
    if not api_key:
        return "OpenAI API key not set."
    try:
        client = openai.OpenAI(api_key=api_key)
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful {role} for student mental health."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"
