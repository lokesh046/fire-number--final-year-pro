# chat_service/tool_executor.py

import httpx

async def execute_tool(tool_name, payload):

    endpoints = {
        "calculate_fire": "http://localhost:8001/fire",
        "calculate_health_score": "http://localhost:8002/health-score",
        "optimize_loan": "http://localhost:8004/loan-analysis"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoints[tool_name], json=payload)
        return response.json()