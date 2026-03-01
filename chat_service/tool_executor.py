# chat_service/tool_executor.py

import httpx

async def execute_tool(tool_name, payload, auth_token: str = None):
    """
    Execute tool by calling internal microservices.
    Supports optional auth_token for authenticated requests.
    """
    
    endpoints = {
        "calculate_fire": "http://localhost:8001/fire",
        "calculate_health_score": "http://localhost:8002/health-score",
        "optimize_loan": "http://localhost:8004/loan-analysis"
    }
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                endpoints[tool_name], 
                json=payload,
                headers=headers,
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}