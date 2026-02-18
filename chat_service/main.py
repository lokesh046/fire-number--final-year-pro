from fastapi import FastAPI
from .models import ChatRequest, ChatResponse
from .llm_client import call_llm
from .tool_executor import execute_tool
from .guardrails import validate_tool_call

app = FastAPI(title="Hybrid AI Chat Agent")

@app.post("/chat-agent", response_model=ChatResponse)
async def chat_agent(data: ChatRequest):
    messages = [{"role": "user", "parts": [{"text": data.message}]}]

    try:
        llm_response = call_llm(messages)
        candidate = llm_response.candidates[0]
        parts = candidate.content.parts

        for part in parts:
            if hasattr(part, "function_call") and part.function_call:
                tool_name = part.function_call.name
                arguments = dict(part.function_call.args)

                valid, message = validate_tool_call(tool_name, arguments)
                if not valid:
                    return ChatResponse(reply=f"Blocked: {message}")

                tool_result = await execute_tool(tool_name, arguments)
                return ChatResponse(
                    reply=f"Executed {tool_name} successfully.",
                    tool_used=tool_name,
                    tool_result=tool_result
                )

        if hasattr(parts[0], "text"):
            return ChatResponse(reply=parts[0].text)

    # main.py
    except Exception as e:
        # Check if it's a rate limit error specifically
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return ChatResponse(
                reply="The AI is at its limit. Please ensure a billing account is linked to your project to activate Free Tier quotas."
            )
        return ChatResponse(reply=f"Unexpected Error: {str(e)}")

