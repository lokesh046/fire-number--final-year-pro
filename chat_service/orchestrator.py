# chat_service/orchestrator.py

from .state import FinancialState
from .financial_interpreter import FinancialInterpreter
from .guardrails import Guardrails
from .planner import Planner
from .execution_engine import ExecutionEngine


class FinancialOrchestrator:

    def __init__(self, llm_client):
        self.interpreter = FinancialInterpreter(llm_client)
        self.guardrails = Guardrails()
        self.planner = Planner()
        self.engine = ExecutionEngine()

    async def handle_request(self, message: str):

        # 1️⃣ Extract structured data from LLM
        extracted_data = await self.interpreter.extract(message)

        print("EXTRACTED DATA:", extracted_data)

        # 2️⃣ Convert to FinancialState
        state = FinancialState(**extracted_data)

        # 3️⃣ Guardrails validation
        self.guardrails.validate(state)

        # 4️⃣ Planning (decide tools)
        tools_to_run = self.planner.create_plan(state)

        print("TOOLS TO RUN:", tools_to_run)

        # 5️⃣ Execute tools
        tool_results = await self.engine.execute(tools_to_run, state)

        # 6️⃣ Update state safely from tool results
        for tool_name, result in tool_results.items():
            if isinstance(result, dict):
                state = state.model_copy(update=result)

        return {
            "state": state.model_dump(),
            "tools_used": tools_to_run,
            "tool_results": tool_results
        }