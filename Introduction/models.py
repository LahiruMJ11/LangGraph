import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Valid Model Names for YOU ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        # This prints the EXACT string you need to use
        print(m.name.replace("models/", ""))