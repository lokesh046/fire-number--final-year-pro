# chat_service/explanation_engine.py

class ExplanationEngine:

    def __init__(self, llm_client):
        self.llm = llm_client

    async def generate(self, state):

        prompt = f"""
        You are a professional financial advisor.

        Explain the financial situation clearly and professionally
        using the computed values below.

        IMPORTANT:
        - Do NOT recalculate anything.
        - Only use the numbers provided.
        - Give practical advice.
        - Keep it structured and easy to understand.

        Financial Data:
        Monthly Income: {state.monthly_income}
        Monthly Expense: {state.living_expense}
        Current Savings: {state.current_savings}
        Loan EMI: {state.loan_emi}
        FIRE Number: {state.fire_number}
        Years to FIRE: {state.fire_year}
        Final Wealth Projection: {state.final_wealth}
        Financial Health Score: {state.financial_health_score}
        """

        explanation = await self.llm.generate_text(prompt)

        return explanation