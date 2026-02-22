# chat_service/execution_engine.py

from .tool_executor import execute_tool

class ExecutionEngine:

    async def execute(self, tools, state):

        results = {}

        for tool in tools:

            payload = state.model_dump()

            # 🔥 Fix insurance type
            if tool == "calculate_health_score":
                if isinstance(payload.get("has_insurance"), bool):
                    payload["has_insurance"] = "yes" if payload["has_insurance"] else "no"

            result = await execute_tool(tool, payload)

            results[tool] = result

            # Update state from successful tool output
            if tool == "calculate_fire" and "fire_number" in result:
                state.fire_number = result["fire_number"]
                state.fire_year = result["fire_year"]
                state.final_wealth = result["final_wealth"]

            if tool == "calculate_health_score" and "financial_health_score" in result:
                state.financial_health_score = result["financial_health_score"]

        return results