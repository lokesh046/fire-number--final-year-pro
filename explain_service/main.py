from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Literal, Optional
import os
import shutil

from .pipeline.retrieval import retrieve
from .pipeline.prompt_builder import build_prompt
from .pipeline.ingestion import ingest_file
from .pipeline.vectordb import collection
from .pipeline.llm_client import generate_explanation
from shared.services.service_auth import get_current_user, CurrentUser

app = FastAPI(
    title="Explain Service",
    description="AI-Powered Financial Strategy Explanation Service"
)

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "super_secret_key_change_me")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ExplainRequest(BaseModel):
    context_type: Literal["loan_fire_strategy"]
    current_fire_year: int
    optimized_fire_year: int
    recommended_emi: float
    strategy_recommendation: str
    financial_health_score: float


class ExplainResponse(BaseModel):
    summary: str
    reasoning_points: list[str]
    risk_note: str
    sources: list[str]
    confidence_score: float


def verify_admin(api_key: str) -> bool:
    """Verify admin API key"""
    if api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )
    return True


def verify_user_or_admin(
    authorization: Optional[str] = Header(None),
    api_key: Optional[str] = Header(None)
) -> CurrentUser:
    """
    Verify either user JWT or admin API key.
    For /explain-strategy: requires user authentication
    For /admin/*: requires admin API key
    """
    if api_key:
        verify_admin(api_key)
        return CurrentUser(
            id="admin",
            email="admin@system",
            role="admin"
        )
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        from shared.services.service_auth import decode_token
        token_data = decode_token(token)
        return CurrentUser(
            id=token_data.user_id,
            email=token_data.email or "",
            role=token_data.role
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )


@app.post("/explain-strategy", response_model=ExplainResponse)
async def explain_strategy(
    data: ExplainRequest,
    user: CurrentUser = Depends(verify_user_or_admin)
):
    """
    Generate AI explanation for financial strategy.
    Requires authentication (JWT or admin API key).
    """
    if not user.is_active and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_DETAIL,
            detail=f"Error generating explanation: {str(e)}"
        )


@app.post("/admin/upload")
async def admin_upload(
    file: UploadFile = File(...),
    api_key: str = Header(...)
):
    """
    Admin endpoint to upload knowledge base documents.
    Requires admin API key.
    """
    verify_admin(api_key)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_file(file_path, file.filename)

    return {
        "status": "Knowledge uploaded",
        "details": result
    }


@app.delete("/admin/delete")
async def admin_delete(
    source: str,
    api_key: str = Header(...)
):
    """
    Admin endpoint to delete knowledge base documents.
    Requires admin API key.
    """
    verify_admin(api_key)

    collection.delete(where={"source": source})

    return {"status": "Deleted successfully"}


@app.get("/health")
def health_check():
    """Public health check endpoint"""
    return {"status": "healthy", "service": "explain_service"}


@app.get("/protected")
def protected_endpoint(user: CurrentUser = Depends(verify_user_or_admin)):
    """Test endpoint to verify authentication"""
    return {
        "message": "You are authenticated!",
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
