from google import genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Read API key
api_key = os.getenv("GEMINI_API_KEY")

print("API KEY:", api_key)

# Create Gemini client
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say Hello World"
    )

    print("\nSUCCESS")
    print(response.text)

except Exception as e:
    print("\nERROR")
    print(e)