from fastapi import FastAPI
from pydantic import BaseModel

from .financial_health_score import calculate_financial_health_score

app = FastAPI(title ="Health Score Service")

class HealthInput(BaseModel):
    monthly_income: float
    living_expense:  float
    loan_emi: float
    current_savings: float
    fire_number: float
    has_insurance: str

@app.post("/health-score")
def calculate_health(data: HealthInput):

    score = calculate_financial_health_score(
        monthly_income=data.monthly_income,
        living_expense=data.living_expense,
        loan_emi=data.loan_emi,
        current_savings=data.current_savings,
        fire_number=data.fire_number,
        has_insurance=data.has_insurance
    )

    return {"financial_health_score": score}
