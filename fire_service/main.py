from fastapi import FastAPI
from pydantic import BaseModel

from .fire_engine import calculate_fire_plan

app = FastAPI(title="Fire Service")

class FireInput(BaseModel):
    monthly_income: float
    living_expense: float
    current_savings: float
    return_rate: float
    inflation_rate: float
    has_loan: bool
    loan_emi: float = 0
    loan_years: int = 0

@app.post("/fire")
def calculate_fire(data: FireInput):

    result = calculate_fire_plan(
        monthly_income=data.monthly_income,
        living_expense=data.living_expense,
        current_savings=data.current_savings,
        return_rate=data.return_rate,
        inflation_rate=data.inflation_rate,
        has_loan=data.has_loan,
        loan_emi=data.loan_emi,
        loan_years=data.loan_years
    )

    return result