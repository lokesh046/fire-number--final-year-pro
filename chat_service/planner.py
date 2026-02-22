# chat_service/planner.py

class Planner:

    def create_plan(self, state):
        """
        Decide which tools to run based on current state.
        """

        tools = []

        # If FIRE not calculated yet → calculate FIRE first
        if state.fire_number is None:
            tools.append("calculate_fire")

        # Always calculate health score after FIRE
        tools.append("calculate_health_score")

        # If loan exists and interest rate provided → optimize loan
        if state.has_loan and state.loan_interest_rate:
            tools.append("optimize_loan")

        return tools
        