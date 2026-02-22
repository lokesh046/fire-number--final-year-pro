# chat_service/financial_interpreter.py

class FinancialInterpreter:

    def __init__(self, llm_client):
        self.llm = llm_client

    async def extract(self, message: str):

        prompt = f"""
        Extract structured financial information from this message.

        Return ONLY valid JSON.
        If a value is missing, return null.

        Fields:
        - monthly_income
        - living_expense
        - current_savings
        - loan_emi
        - loan_years
        - loan_interest_rate
        - has_loan
        - has_insurance

        Message:
        {message}
        """

        data = await self.llm.extract_json(prompt)

# 🔥 FIX: Normalize insurance to string
        if "has_insurance" in data:
            if data["has_insurance"] is True:
                data["has_insurance"] = "yes"
            elif data["has_insurance"] is False:
                data["has_insurance"] = "no"

        return data