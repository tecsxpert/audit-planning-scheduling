import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "ai-service"))

from services.groq_client import GroqClient, GroqError

client = GroqClient()

try:
    result = client.generate_response("Tell me about AI")
    print(result)
except GroqError as error:
    print("Groq test failed:", error)
