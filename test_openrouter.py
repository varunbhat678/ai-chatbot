from openai import OpenAI

from app.config.settings import OPENROUTER_API_KEY


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


try:
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one short sentence."
            }
        ]
    )

    print("SUCCESS!")
    print(response.choices[0].message.content)

except Exception as e:
    print("OPENROUTER ERROR:")
    print(e)