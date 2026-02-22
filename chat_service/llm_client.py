# chat_service/llm_client.py

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def generate(self, prompt: str):

        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )

        return response.text

    async def extract_json(self, prompt: str):
        """
        Forces LLM to return clean JSON
        """

        system_prompt = f"""
You are a financial data extraction engine.

Return ONLY valid JSON.
Do not explain.
Do not add text.
Do not use markdown.

{prompt}
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )

        text = response.text.strip()

        try:
            return json.loads(text)
        except:
            print("RAW LLM RESPONSE:", text)
            raise Exception("LLM did not return valid JSON")