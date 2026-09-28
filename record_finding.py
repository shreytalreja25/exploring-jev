import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY", "")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not set.")

with OpenRouter(api_key=api_key) as client:
    response = client.chat.send(
        model="typesafe/jev-router",
        messages=[
            {
                "role": "user",
                "content": "Which model are you?",
            }
        ],
    )

print("=" * 60)
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"Requested Model: typesafe/jev-router")
print(f"Underlying Routed Model: {response.model}")
print(f"Assistant Content: {response.choices[0].message.content}")
print(f"Generation ID: {response.id}")
print(f"Token Usage: {response.usage}")
print("=" * 60)
