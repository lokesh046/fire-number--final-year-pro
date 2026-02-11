# -------- main.py --------

# IMPORT MODULES
from user_input import get_user_finance_input
from fire_number import calculate_fire_plan
from financial_health_score import calculate_financial_health_score


# 1️⃣ GET USER INPUT
data = get_user_finance_input()


# 2️⃣ FIRE CALCULATION
fire_result = calculate_fire_plan(
    monthly_income=data["monthly_income"],
    living_expense=data["living_expense"],
    current_savings=data["current_savings"],
    return_rate=data["return_rate"],
    inflation_rate=data["inflation_rate"],
    has_loan=data["has_loan"],
    loan_emi=data["loan_emi"],
    loan_years=data["loan_years"]
)


# 3️⃣ FINANCIAL HEALTH SCORE
health_score = calculate_financial_health_score(
    monthly_income=data["monthly_income"],
    living_expense=data["living_expense"],
    loan_emi=data["loan_emi"],
    current_savings=data["current_savings"],
    fire_number=fire_result["fire_number"],
     has_insurance=data["has_insurance"]
)


# 4️⃣ PRINT FINAL RESULT
print("\n================= WEALTH TO FIRE RESULT =================")

print(f"🔥 FIRE Number        : {round(fire_result['fire_number'],2)}")
print(f"📆 FIRE Achieved In   : {fire_result['fire_year']} years")
print(f"💰 Final Wealth       : {fire_result['final_wealth']}")

print("\n📊 Financial Health Score :", round(health_score,2), "/ 100")

print("==========================================================")
