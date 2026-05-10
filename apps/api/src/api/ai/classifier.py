import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from api.ai.schemas import TicketClassification

load_dotenv()  # Load environment variables from .env file

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify(text: str) -> TicketClassification:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TicketClassification,
            system_instruction="Predict between 1 and 4 tags from the provided list. Include only tags clearly supported by the ticket text. Order by relevance, most relevant first.",
        ),
    )
    return response.parsed
