import math

def validate_loan_inputs(loan_amount, annual_interest_rate, tenure_years):

    if loan_amount <= 0:
        raise ValueError("Loan amount must be greater than 0.")

    if annual_interest_rate <= 0 or annual_interest_rate > 0.5:
        raise ValueError("Interest rate must be between 0 and 50%.")

    if tenure_years <= 0 or tenure_years > 40:
        raise ValueError("Tenure must be between 1 and 40 years.")

def normalize_interest_rate(rate_value, rate_type):
    """
    Converts interest rate to annual rate.
    """

    if rate_type == "annual":
        annual_rate = rate_value

    elif rate_type == "monthly":
        annual_rate = rate_value * 12

    else:
        raise ValueError("rate_type must be 'annual' or 'monthly'.")

    # Safety check
    if annual_rate <= 0 or annual_rate > 0.5:
        raise ValueError("Annual interest must be between 0% and 50%.")

    return annual_rate


#EMI calculating 
def calculate_emi(loan_amount, annual_interest_rate, tenure_years):
    validate_loan_inputs(loan_amount, annual_interest_rate, tenure_years)

    monthly_rate = annual_interest_rate / 12
    months = tenure_years * 12

    # EMI formula
    emi = (
        loan_amount * monthly_rate * (1 + monthly_rate) ** months
    ) / ((1 + monthly_rate) ** months - 1)

    return round(emi, 2)



## calculating the interest their paid 

def generate_amortization_schedule(loan_amount, annual_interest_rate, emi):

    monthly_rate = annual_interest_rate / 12

    if emi <= 0:
        raise ValueError("EMI must be greater than 0.")

    min_emi_required = loan_amount * monthly_rate

    if emi <= min_emi_required:
        raise ValueError(
            f"EMI too low. Minimum EMI must be greater than {round(min_emi_required,2)}"
        )

    #
    if emi > loan_amount:
        raise ValueError("EMI is unrealistically high compared to loan amount.")


    monthly_rate = annual_interest_rate / 12
    balance = loan_amount
    month = 0
    total_interest = 0

    max_month_limit = 1000  # safety guard

    schedule = []

    while balance > 0 and month < max_month_limit:

        month += 1

        interest = balance * monthly_rate
        principal = emi - interest

        # Prevent negative principal case
        if principal <= 0:
            raise ValueError("EMI too low. Loan will never be repaid.")

        # Final month adjustment
        if principal > balance:
            principal = balance
            emi = interest + principal

        balance -= principal
        total_interest += interest

        schedule.append({
            "month": month,
            "principal_paid": round(principal, 2),
            "interest_paid": round(interest, 2),
            "remaining_balance": round(balance, 2)
        })

    if month >= max_month_limit:
        raise ValueError("Loan repayment exceeds safe simulation limit.")

    return {
        "months_to_payoff": month,
        "total_interest_paid": round(total_interest, 2),
        "schedule": schedule
    }

def suggest_optimal_emi(loan_amount, annual_interest_rate, tenure_years):

    base_emi = calculate_emi(
        loan_amount,
        annual_interest_rate,
        tenure_years
    )

    increments = [0, 0.1, 0.2, 0.3]  # include base EMI
    results = []

    for inc in increments:

        test_emi = base_emi * (1 + inc)

        schedule_data = generate_amortization_schedule(
            loan_amount,
            annual_interest_rate,
            test_emi
        )

        results.append({
            "emi": round(test_emi, 2),
            "months_to_payoff": schedule_data["months_to_payoff"],
            "total_interest_paid": schedule_data["total_interest_paid"]
        })

    # Optimization criteria:
    # Choose EMI that minimizes total interest
    recommended = min(results, key=lambda x: x["total_interest_paid"])

    return {
        "emi_options": results,
        "recommended_option": recommended
    }