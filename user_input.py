def get_user_finance_input():
    print("\n --- enter your financial details --- ")

    data = {}

    #basic finance

    data["monthly_income"] = float(input("Enter monthly income: "))
    data["living_expense"] = float(input("Enter monthly living expense: "))
    data["current_savings"] = float(input("Enter current saving: "))

    #Inverstment assumptions
    data["return_rate"] = float(input("Enter expected return rate (0.10 for 10%): "))
    data["inflation_rate"] = float(input("Enter inflation rate (0.06 for 6%): "))\

    # insurance score
    data["has_insurance"] = input("Enter if you have insurance like (yes/no): ").lower()

    # Loan option
    has_loan = input("Do you have a loan? (yes/no): ").lower()
    data["has_loan"] = has_loan

    
    if has_loan == "yes":
        data["loan_emi"] = float(input("Enter EMI amount: "))
        data["loan_years"] = int(input("Enter loan tenure in years: "))
    else:
        data["loan_emi"] = 0.0
        data["loan_years"] = 0

    return data