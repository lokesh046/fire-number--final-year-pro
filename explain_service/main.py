from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
from typing import Literal
import os
import shutil

from pipeline.retrieval import retrieve
from pipeline.prompt_builder import build_prompt
from pipeline.ingestion import ingest_file
from pipeline.vectordb import collection
from pipeline.llm_client import generate_explanation


app = FastAPI(title="Explain Service")

ADMIN_API_KEY = "super_secret_key"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------
# 🔹 Request Models
# -------------------------

class ExplainRequest(BaseModel):
    context_type: Literal["loan_fire_strategy"]
    current_fire_year: int
    optimized_fire_year: int
    recommended_emi: float
    strategy_recommendation: str
    financial_health_score: float


# -------------------------
# 🔓 PUBLIC ENDPOINT
# -------------------------
class ExplainResponse(BaseModel):
    summary: str
    reasoning_points: list[str]
    risk_note: str
    sources: list[str]
    confidence_score: float


@app.post("/explain-strategy",response_model=ExplainResponse)
async def explain_strategy(data: ExplainRequest):
    
    try:
        query = f"{data.strategy_recommendation} fire timeline debt impact"

        context, sources, confidence = retrieve(query)

        prompt = build_prompt(context, data)

        explanation_structured = await generate_explanation(prompt)

        return {
            **explanation_structured,
            "sources": sources,
            "confidence_score": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# 🔒 ADMIN AUTH CHECK
# -------------------------

def verify_admin(api_key: str):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


# -------------------------
# 🔒 ADMIN UPLOAD
# -------------------------

@app.post("/admin/upload")
async def admin_upload(
    file: UploadFile = File(...),
    api_key: str = Header(...)
):

    verify_admin(api_key)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_file(file_path, file.filename)

    return {
        "status": "Knowledge uploaded",
        "details": result
    }


# -------------------------
# 🔒 ADMIN DELETE
# -------------------------

@app.delete("/admin/delete")
async def admin_delete(
    source: str,
    api_key: str = Header(...)
):

    verify_admin(api_key)

    collection.delete(where={"source": source})

    return {"status": "Deleted successfully"}
