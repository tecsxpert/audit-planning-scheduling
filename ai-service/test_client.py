from services.groq_client import GroqClient, GroqError

client = GroqClient()

try:
    result = client.generate_response("Tell me about AI")
    print(result)
except GroqError as error:
    print("Groq test failed:", error)
