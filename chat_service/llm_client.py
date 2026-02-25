# chat_service/llm_client.py

import re
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class LLMClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    # -------------------------------------------------
    # 1️⃣ Extract JSON (Used by Interpreter)
    # -------------------------------------------------
    async def extract_json(self, prompt: str):

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0
            )
        )

        text = response.text

        # 🔥 REMOVE markdown code blocks if present
        if text.startswith("```"):
            text = re.sub(r"```json", "", text)
            text = re.sub(r"```", "", text)
            text = text.strip()

        # Now safely parse
        return json.loads(text)
    # -------------------------------------------------
    # 2️⃣ Generate Plain Text (Used by Explanation Layer)
    # -------------------------------------------------
    async def generate_text(self, prompt: str):

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7
            )
        )

        return response.text