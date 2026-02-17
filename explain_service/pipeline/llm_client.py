import os
import httpx
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct"

LLM_CACHE = {}



async def generate_explanation(prompt: str):
    """
    Calls OpenRouter and returns structured output compatible with FastAPI response model.
    Includes:
    - Markdown JSON cleaning
    - Flexible structure normalization
    - Strict output enforcement
    - Safe fallback
    """

    # 🔐 Cache key
    cache_key = hashlib.sha256(prompt.encode()).hexdigest()

    if cache_key in LLM_CACHE:
        return LLM_CACHE[cache_key]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional financial advisor.\n"
                    "Return STRICT JSON only with this structure:\n"
                    "{\n"
                    "  \"summary\": \"string\",\n"
                    "  \"reasoning_points\": [\"string\"],\n"
                    "  \"risk_note\": \"string\"\n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            print("OpenRouter Error:", response.status_code, response.text)
            return _fallback_response()

        response_data = response.json()
        raw_output = response_data["choices"][0]["message"]["content"].strip()

        # 🔥 STRONG JSON EXTRACTION
        if "```" in raw_output:
            parts = raw_output.split("```")
            if len(parts) >= 2:
                raw_output = parts[1]

        raw_output = raw_output.strip()

        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:].strip()

        # 🔥 Try parsing JSON
        try:
            structured_output = json.loads(raw_output)
        except json.JSONDecodeError:
            print("JSON parse failed. Raw output:", raw_output)
            structured_output = {
                "summary": raw_output,
                "reasoning_points": [],
                "risk_note": ""
            }

        # 🔥 Ensure keys exist
        structured_output.setdefault("summary", "")
        structured_output.setdefault("reasoning_points", [])
        structured_output.setdefault("risk_note", "")

        # 🔥 Normalize reasoning_points to List[str]
        normalized_points = []

        for point in structured_output["reasoning_points"]:
            if isinstance(point, dict):
                key_point = point.get("key_point", "")
                context = point.get("context", "")
                combined = f"{key_point} {context}".strip()
                normalized_points.append(combined)
            else:
                normalized_points.append(str(point))

        structured_output["reasoning_points"] = normalized_points

        # 🔥 Normalize risk_note to string
        if isinstance(structured_output["risk_note"], dict):
            explanation = structured_output["risk_note"].get("explanation", "")
            suggested_action = structured_output["risk_note"].get("suggested_action", "")
            structured_output["risk_note"] = f"{explanation} {suggested_action}".strip()
        else:
            structured_output["risk_note"] = str(structured_output["risk_note"])

        # 🔥 Final strict output
        final_output = {
            "summary": str(structured_output["summary"]),
            "reasoning_points": structured_output["reasoning_points"],
            "risk_note": structured_output["risk_note"]
        }

        # Store in cache
        LLM_CACHE[cache_key] = final_output

        return final_output

    except Exception as e:
        print("LLM Exception:", str(e))
        return _fallback_response()


def _fallback_response():
    return {
        "summary": "AI explanation temporarily unavailable.",
        "reasoning_points": [],
        "risk_note": ""
    }