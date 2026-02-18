from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

from .loan_engine import (calculate_emi,
generate_amortization_schedule,
suggest_optimal_emi,
normalize_interest_rate
)

app = FastAPI(
    title = "Advance Loan optimier severice ",
    version="2.0"
)

## Request Model
class LoanInput(BaseModel):
    loan_amount: float = Field(..., gt=0)
    interest_rate_value: float = Field(..., gt=0)
    rate_type: str = Field(..., pattern="^(annual|monthly)$")
    tenure_years: int = Field(..., gt=0)


class EMIOption(BaseModel):
    emi: float
    months_to_payoff: int
    total_interest_paid: float


class OptimizationResult(BaseModel):
    emi_options: List[EMIOption]
    recommended_option: EMIOption


## Response Model
class LoanResponse(BaseModel):
    calculated_emi: float
    months_to_payoff: int
    total_interest_paid: float
    optimal_emi_suggestions: OptimizationResult
 


@app.post("/loan-analysis",response_model=LoanResponse)
def analyze_loan(data: LoanInput):
    
    try:
        annual_rate = normalize_interest_rate(
            data.interest_rate_value,
            data.rate_type
        )

        # Calculate EMI
        emi = calculate_emi(
            data.loan_amount,
            annual_rate,
            data.tenure_years
        )

        # Generate amortization schedule
        amortization = generate_amortization_schedule(
            data.loan_amount,
            annual_rate,
            emi
        )

        # Get optimized EMI suggestions
        optimization = suggest_optimal_emi(
            data.loan_amount,
            annual_rate ,
            data.tenure_years
        )

        emi_options = [
            EMIOption(**option)
            for option in optimization["emi_options"]
        ]

        recommended = EMIOption(**optimization["recommended_option"])

        return LoanResponse(
            calculated_emi=emi,
            months_to_payoff=amortization["months_to_payoff"],
            total_interest_paid=amortization["total_interest_paid"],
            optimal_emi_suggestions=OptimizationResult(
                emi_options=emi_options,
                recommended_option=recommended
            )
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

