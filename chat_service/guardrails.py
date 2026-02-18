# chat_service/guardrails.py

ALLOWED_TOOLS = ["calculate_fire", "optimize_loan"]

def validate_tool_call(tool_name: str, arguments: dict):
    if tool_name not in ALLOWED_TOOLS:
        return False, "Tool not allowed."

    if tool_name == "calculate_fire":
        # 1. FIX THE 422 ERROR: Convert Boolean/Missing to String "yes"/"no"
        loan_val = arguments.get("has_loan")
        
        # If it's a boolean False or missing, make it "no"
        if loan_val is False or loan_val is None:
            arguments["has_loan"] = "no"
        # If it's a boolean True, make it "yes"
        elif loan_val is True:
            arguments["has_loan"] = "yes"
        # If it's already a string, ensure it's lowercase
        elif isinstance(loan_val, str):
            arguments["has_loan"] = loan_val.lower()

        # 2. FIX PERCENTAGES: Convert 10 -> 0.1
        for field in ["return_rate", "inflation_rate"]:
            val = arguments.get(field, 0)
            if val > 1: 
                arguments[field] = val / 100

        # 3. REQUIRED FIELDS CHECK
        required = ["monthly_income", "living_expense", "current_savings", "return_rate", "inflation_rate"]
        for field in required:
            if field not in arguments:
                return False, f"Missing {field}"

    return True, "Valid tool call."

