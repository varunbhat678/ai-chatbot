from google import genai
from app.config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    if "generateContent" in getattr(model, "supported_actions", []):
        print(model.name)