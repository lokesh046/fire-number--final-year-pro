import os
import random
import time
from typing import List, Union
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)

load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Decorator to handle 429 Rate Limits automatically
@retry(
    wait=wait_random_exponential(min=2, max=60), # Wait 2s, then 4s, 8s... up to 60s
    stop=stop_after_attempt(5),                  # Try up to 5 times before failing
    retry=retry_if_exception_type(ClientError),  # Only retry on API errors like 429
    reraise=True
)
def call_llm(messages: Union[str, List[dict]]):
    """
    Calls Gemini with full tool definitions and automatic retry logic for 429 errors.
    """
    
    # 1. Full Tool Definitions (Fixes your "Field required" backend error)
    tools = [
        {
            "function_declarations": [
                {
                    "name": "calculate_fire",
                    "description": "Calculate FIRE timeline based on income, expenses, and savings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "monthly_income": {"type": "number"},
                            "living_expense": {"type": "number"},
                            "current_savings": {"type": "number"},
                            "return_rate": {"type": "number", "description": "Annual return e.g. 0.1"},
                            "inflation_rate": {"type": "number", "description": "Annual inflation e.g. 0.06"},
                            # ADDED: This matches your backend's required field
                            "has_loan": {"type": "boolean", "description": "Whether the user has an active loan"}
                        },
                        "required": [
                            "monthly_income", "living_expense", "current_savings", 
                            "return_rate", "inflation_rate"
                        ]
                    }
                },
                {
                    "name": "optimize_loan",
                    "description": "Optimize loan EMI and tenure.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "loan_amount": {"type": "number"},
                            "interest_rate_value": {"type": "number"},
                            "rate_type": {"type": "string"},
                            "tenure_years": {"type": "number"}
                        },
                        "required": ["loan_amount", "interest_rate_value", "rate_type", "tenure_years"]
                    }
                }
            ]
        }
    ]

    # 2. API Call with Config
    # Using 'gemini-1.5-flash' can sometimes have better quota availability than 2.0-flash
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0.7 # Lower temperature is better for consistent tool calling
        )
    )

    return response
