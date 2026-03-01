# chat_service/orchestrator.py

from .financial_state import FinancialState
from .financial_interpreter import FinancialInterpreter
from .financial_sanity import FinancialSanityEngine
from .guardrails import Guardrails
from .planner import Planner
from .execution_engine import ExecutionEngine
from .explanation_engine import ExplanationEngine


class FinancialOrchestrator:

    def __init__(self, llm_client):
        self.interpreter = FinancialInterpreter(llm_client)
        self.planner = Planner(llm_client)
        self.executor = ExecutionEngine()
        self.explainer = ExplanationEngine(llm_client)
        self.guardrails = Guardrails()
        self.sanity = FinancialSanityEngine()

    async def handle_request(self, message, auth_token: str = None):

        # 1️⃣ Extract financial data
        extracted_data = await self.interpreter.extract(message)

        # 2️⃣ Create state
        state = FinancialState()
        state.__dict__.update(extracted_data)
        # 🔥 Ensure default investment assumptions
        if state.return_rate is None:
            state.return_rate = 0.10

        if state.inflation_rate is None:
            state.inflation_rate = 0.06

        # 3️⃣ Hard validation
        self.guardrails.validate(state)

        # 4️⃣ Sanity validation
        valid, warnings = self.sanity.validate(state)

        if not valid:
            return {
                "error": "Invalid financial input",
                "details": warnings
            }

        # 5️⃣ Tool Planning
        tools_to_run = await self.planner.create_plan(state)

        tool_results = {}

        # 6️⃣ Execute Tools (with auth token)
        if tools_to_run:
            state, tool_results = await self.executor.execute_chain(
                tools_to_run,
                state,
                auth_token
            )

        # 7️⃣ Explanation
        explanation = await self.explainer.generate(state)

        return {
            "state": state.to_dict(),
            "tools_used": tools_to_run,
            "tool_results": tool_results,
            "advisor_explanation": explanation,
            "flags": state.flags
        }