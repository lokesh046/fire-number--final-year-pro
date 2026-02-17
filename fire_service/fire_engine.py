# -------- fire_engine.py --------

def calculate_fire_plan(
    monthly_income: float,
    living_expense: float,
    current_savings: float,
    return_rate: float,
    inflation_rate: float,
    has_loan: str,
    loan_emi: float = 0,
    loan_years: int = 0
):
    """
    Calculates FIRE Number, Years to FIRE, and Final Wealth
    """

    #REAL RETURN 
    real_return_rate = ((1 + return_rate) / (1 + inflation_rate)) - 1

    # FIRE NUMBER
    annual_expense = living_expense * 12
    fire_number = annual_expense * 25 #SWP - Smart withdrawl plan 

    #BASE SAVINGS 
    base_monthly_savings = monthly_income - living_expense

    if base_monthly_savings <= 0:
        return {
            "fire_number": fire_number,
            "fire_year": "Not Achievable",
            "final_wealth": current_savings
        }


    wealth = current_savings
    year = 0
    max_year_limit = 100

    #  FIRE SIMULATION
    while wealth < fire_number and year <= max_year_limit:

        year += 1

        # Loan phase
        if has_loan == "yes" and year <= loan_years:
            monthly_savings = base_monthly_savings - loan_emi
        else:
            monthly_savings = base_monthly_savings

        annual_savings = monthly_savings * 12

        wealth = (wealth + annual_savings) * (1 + real_return_rate)

    if year >= max_year_limit :
        return {
            "fire_number": fire_number,
            "fire_year": "Beyond 100 years",
            "final_wealth": round(wealth, 2)
        }

    
    return {
        "fire_number": fire_number,
        "fire_year": year,
        "final_wealth": round(wealth, 2)
    }