from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="AI Explain Service")


class ExplainRequest(BaseModel):
    context_type: Literal["loan_fire_strategy"]
    current_fire_year: int
    optimized_fire_year: int
    recommended_emi: float
    strategy_recommendation: Literal["increase_emi", "keep_current_emi"]
    financial_health_score: float


class ExplainResponse(BaseModel):
    explanation: str


@app.post("/explain-strategy", response_model=ExplainResponse)
async def explain_strategy(data: ExplainRequest):

    # Placeholder for RAG + LLM logic
    explanation_text = "Explanation will be generated here."

    return ExplainResponse(explanation=explanation_text)
