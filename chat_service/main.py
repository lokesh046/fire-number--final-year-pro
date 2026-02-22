# chat_service/main.py

from fastapi import FastAPI
from pydantic import BaseModel

from .orchestrator import FinancialOrchestrator
from .llm_client import LLMClient


app = FastAPI()


class ChatRequest(BaseModel):
    message: str


# Create LLM
llm_client = LLMClient()

# Inject into orchestrator
orchestrator = FinancialOrchestrator(llm_client)


@app.post("/chat-agent")
async def chat_agent(data: ChatRequest):

    result = await orchestrator.handle_request(data.message)

    return result