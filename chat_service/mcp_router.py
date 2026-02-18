def route_query(message: str) -> str:

    message = message.lower()

    if "fire number" in message or "retire" in message:
        return "fire"

    elif "strategy" in message or "emi" in message:
        return "strategy"

    else:
        return "general"
