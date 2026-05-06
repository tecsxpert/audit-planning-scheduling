import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq_connection():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key":
        print("Please set a valid GROQ_API_KEY in .env")
        return

    try:
        print("Testing Groq API connection...")
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Please reply with exactly 'Groq connection successful' if you can read this.",
                }
            ],
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            max_tokens=20,
        )
        
        result = response.choices[0].message.content.strip()
        print(f"Response from Groq: {result}")
        if "successful" in result.lower():
            print("Smoke test passed successfully!")
        else:
            print("Unexpected response received, but connection works.")
            
    except Exception as e:
        print(f"Error connecting to Groq API: {e}")

if __name__ == "__main__":
    test_groq_connection()
