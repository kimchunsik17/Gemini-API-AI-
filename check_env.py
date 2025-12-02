import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key is missing/empty.")
else:
    print(f"API Key length: {len(api_key)}")
    print(f"Starts with: '{api_key[:4]}...'")
    print(f"Ends with: '...{api_key[-4:]}'")
    
    if "YOUR_GEMINI_API_KEY_HERE" in api_key:
        print("WARNING: The placeholder text is still present in the API key.")
    
    if api_key.startswith(" ") or api_key.endswith(" "):
        print("WARNING: API Key has leading or trailing whitespace.")
    
    if '"' in api_key or "'" in api_key:
        print("WARNING: API Key contains quotes within the value string (this might be intentional but check .env parsing).")
