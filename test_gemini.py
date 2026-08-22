from google import genai
from app.config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one sentence."
    )

    print("SUCCESS!")
    print(response.text)

except Exception as e:
    print("GEMINI ERROR:")
    print(e)