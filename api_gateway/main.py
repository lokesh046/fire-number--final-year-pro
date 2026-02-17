from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI(title="Wealth To FIRE Gateway (Async)")


class FinanceInput(BaseModel):
    monthly_income: float
    living_expense: float
    current_savings: float
    return_rate: float
    inflation_rate: float
    has_loan: str
    loan_amount: float
    interest_rate_value: float
    rate_type: str
    loan_emi: float = 0
    loan_years: int = 0
    has_insurance: str

class LoanOnlyInput(BaseModel):
    loan_amount: float
    interest_rate_value: float
    rate_type: str
    tenure_years: int

@app.post("/calculate-fire")
async def calculate_fire(data: FinanceInput):

    async with httpx.AsyncClient() as client:

        fire_response = await client.post(
            "http://localhost:8001/fire",
            json=data.dict()
        )

        if fire_response.status_code != 200:
            return {
                "error": "FIRE service failed",
                "details": fire_response.text
            }

        fire_data = fire_response.json()

        health_response = await client.post(
            "http://localhost:8002/health-score",
            json={
                "monthly_income": data.monthly_income,
                "living_expense": data.living_expense,
                "loan_emi": data.loan_emi,
                "current_savings": data.current_savings,
                "fire_number": fire_data["fire_number"],
                "has_insurance": data.has_insurance
            }
        )

        if health_response.status_code != 200:
            return {
                "error": "Health service failed",
                "details": health_response.text
            }

        health_data = health_response.json()

    return {
        "fire_number": fire_data["fire_number"],
        "fire_year": fire_data["fire_year"],
        "final_wealth": fire_data["final_wealth"],
        "financial_health_score": health_data["financial_health_score"]
    }


@app.post("/loan-fire-strategy")
async def compare_loan_vs_fire(data: FinanceInput):

    async with httpx.AsyncClient() as client:

        # 1️⃣ Get loan optimization suggestions
        loan_response = await client.post(
            "http://localhost:8004/loan-analysis",
            json={
                "loan_amount": data.loan_emi * data.loan_years * 12,
                "interest_rate_value": data.return_rate,
                "rate_type": "annual",
                "tenure_years": data.loan_years
            }
        )

        loan_data = loan_response.json()

        # Get recommended EMI
        recommended_emi = loan_data["optimal_emi_suggestions"]["recommended_option"]["emi"]

        # 2️⃣ FIRE with current EMI
        fire_current = await client.post(
            "http://localhost:8001/fire",
            json=data.dict()
        )

        fire_current_data = fire_current.json()

        # 3️⃣ FIRE with optimized EMI
        modified_data = data.dict()
        modified_data["loan_emi"] = recommended_emi

        fire_optimized = await client.post(
            "http://localhost:8001/fire",
            json=modified_data
        )

        fire_optimized_data = fire_optimized.json()

            # Determine strategy
        strategy = (
            "increase_emi"
            if fire_optimized_data["fire_year"] < fire_current_data["fire_year"]
            else "keep_current_emi"
        )

        # 🔥 Call Explain Service
        explain_response = await client.post(
            "http://localhost:8005/explain-strategy",
            json={
                "context_type": "loan_fire_strategy",
                "current_fire_year": fire_current_data["fire_year"],
                "optimized_fire_year": fire_optimized_data["fire_year"],
                "recommended_emi": recommended_emi,
                "strategy_recommendation": strategy,
                "financial_health_score": 70  # replace with actual health score if available
            }
        )

        explain_data = explain_response.json()

    # Final Response
    return {
        "current_fire_year": fire_current_data["fire_year"],
        "optimized_fire_year": fire_optimized_data["fire_year"],
        "recommended_emi": recommended_emi,
        "strategy_recommendation": strategy,
        "ai_explanation": explain_data["explanation"]
    }


# LOAN ONLY
@app.post("/loan-only")
async def loan_only(data: LoanOnlyInput):

    async with httpx.AsyncClient() as client:

        response = await client.post(
            "http://localhost:8004/loan-analysis",
            json=data.dict()
        )

        return response.json()












































































































# # -------- main.py --------

# # IMPORT MODULES
# from user_input import get_user_finance_input
# from fire_number import calculate_fire_plan
# from financial_health_score import calculate_financial_health_score


# # 1️⃣ GET USER INPUT
# data = get_user_finance_input()


# # 2️⃣ FIRE CALCULATION
# fire_result = calculate_fire_plan(
#     monthly_income=data["monthly_income"],
#     living_expense=data["living_expense"],
#     current_savings=data["current_savings"],
#     return_rate=data["return_rate"],
#     inflation_rate=data["inflation_rate"],
#     has_loan=data["has_loan"],
#     loan_emi=data["loan_emi"],
#     loan_years=data["loan_years"]
# )


# # 3️⃣ FINANCIAL HEALTH SCORE
# health_score = calculate_financial_health_score(
#     monthly_income=data["monthly_income"],
#     living_expense=data["living_expense"],
#     loan_emi=data["loan_emi"],
#     current_savings=data["current_savings"],
#     fire_number=fire_result["fire_number"],
#      has_insurance=data["has_insurance"]
# )


# # 4️⃣ PRINT FINAL RESULT
# print("\n================= WEALTH TO FIRE RESULT =================")

# print(f"🔥 FIRE Number        : {round(fire_result['fire_number'],2)}")
# print(f"📆 FIRE Achieved In   : {fire_result['fire_year']} years")
# print(f"💰 Final Wealth       : {fire_result['final_wealth']}")

# print("\n📊 Financial Health Score :", round(health_score,2), "/ 100")

# print("==========================================================")
