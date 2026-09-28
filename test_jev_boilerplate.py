import os
import traceback
from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY", "")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not set.")

print("[*] Running verbatim OpenRouter boilerplate against typesafe/jev-router...")

try:
    with OpenRouter(api_key=api_key) as client:
        response = client.chat.send(
            model="typesafe/jev-router",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Which model are you?",
                        },
                    ],
                }
            ],
        )
        print("[+] Success (unexpected):", response.choices[0].message.content)

except Exception as exc:
    print("\n[-] Caught expected error:")
    print(f"Exception Type: {type(exc).__name__}")
    print(f"Error Message: {exc}")
    print("\n--- Full Traceback ---")
    traceback.print_exc()
