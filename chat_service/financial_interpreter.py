# chat_service/financial_interpreter.py

import re
import json


class FinancialInterpreter:

    def __init__(self, llm_client):
        self.llm = llm_client

    # -------------------------------------------------
    # WORD → NUMBER CONVERTER (SAFE VERSION)
    # -------------------------------------------------
    def word_to_number(self, text: str):

        number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12,
            "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70,
            "eighty": 80, "ninety": 90
        }

        multipliers = {
            "hundred": 100,
            "thousand": 1000,
            "lakh": 100000,
            "lakhs": 100000
        }

        words = text.lower().split()

        total = 0
        current = 0

        for word in words:
            if word in number_words:
                current += number_words[word]
            elif word in multipliers:
                current = max(1, current) * multipliers[word]
                total += current
                current = 0
            else:
                # stop at unrelated words
                break

        total += current
        return total if total > 0 else None

    # -------------------------------------------------
    # SAFE NUMBER EXTRACTION
    # -------------------------------------------------
    def extract_number_phrase(self, pattern, message):
        match = re.search(pattern, message, re.IGNORECASE)
        if not match:
            return None

        value = match.group(1).strip()

        # If numeric
        if re.fullmatch(r"\d+", value):
            return float(value)

        # If word-number
        return self.word_to_number(value)

    # -------------------------------------------------
    # MAIN EXTRACTION
    # -------------------------------------------------
    async def extract(self, message: str):

        # -----------------------------
        # Improved patterns
        # -----------------------------

        income_pattern = r"(?:earn|salary|take home|income).*?([a-zA-Z\s]+?\s?(?:thousand|lakh|lakhs|\d+))"
        expense_pattern = r"(?:spend|expense|bills|goes for|expenses).*?([a-zA-Z\s]+?\s?(?:thousand|lakh|lakhs|\d+))"
        savings_pattern = r"(?:saving|savings|put aside|aside).*?([a-zA-Z\s]+?\s?(?:thousand|lakh|lakhs|\d+))"
        emi_pattern = r"(?:emi|loan payment|installment).*?([a-zA-Z\s]+?\s?(?:thousand|lakh|lakhs|\d+))"
        years_pattern = r"(?:for|another).*?([a-zA-Z\s]+?)\s+(?:years|yrs)"

        data = {
            "monthly_income": self.extract_number_phrase(income_pattern, message),
            "living_expense": self.extract_number_phrase(expense_pattern, message),
            "current_savings": self.extract_number_phrase(savings_pattern, message),
            "loan_emi": self.extract_number_phrase(emi_pattern, message),
            "loan_years": self.extract_number_phrase(years_pattern, message),
        }

        # -----------------------------
        # LLM fallback if needed
        # -----------------------------
        missing = [k for k, v in data.items() if v is None]

        if len(missing) >= 2:

            prompt = f"""
            Extract structured financial data from this text.

            Convert words to numbers:
            - sixty thousand → 60000
            - two lakhs → 200000
            - five years → 5

            Return STRICT JSON only.

            Text:
            {message}

            {{
                "monthly_income": number or null,
                "living_expense": number or null,
                "current_savings": number or null,
                "loan_emi": number or null,
                "loan_years": number or null,
                "has_insurance": "yes" or "no"
            }}
            """

            llm_data = await self.llm.extract_json(prompt)

            if isinstance(llm_data, str):
                llm_data = json.loads(llm_data)

            if isinstance(llm_data, dict):
                data.update(llm_data)

        # -----------------------------
        # Normalization
        # -----------------------------
        data["has_loan"] = True if data.get("loan_emi") else False
        data["has_insurance"] = data.get("has_insurance", "no")

        return data