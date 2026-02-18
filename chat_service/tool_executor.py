# chat_service/tool_executor.py
import httpx

async def execute_tool(tool_name: str, arguments: dict):
    endpoints = {
        "calculate_fire": "http://localhost:8001/fire",
        "optimize_loan": "http://localhost:8004/loan-analysis"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(endpoints[tool_name], json=arguments, timeout=10.0)
            response.raise_for_status() # Raises error for 4xx/5xx
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # RETURN THE ACTUAL VALIDATION ERROR FROM BACKEND
            return {
                "error": f"Service returned {e.response.status_code}", 
                "details": e.response.json() # <--- This reveals the missing field or wrong value
            }
            
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}
