from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .orchestrator import FinancialOrchestrator
from .llm_client import LLMClient


from shared.database import get_db, engine, Base
import shared.models  # IMPORTANT: registers models

from shared.services.auth_routes import router as auth_router
from shared.services.auth import get_current_user
from shared.services.fire_service import save_fire_calculation
from shared.models.user import User
from shared.services.dashboard_routes import router as dashboard_router


app = FastAPI(title="AI Financial Planning Platform")

# Include Auth Routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard_router, tags=["Dashboard"])


@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database connection established and tables created")
    except TimeoutError:
        print("⚠️  WARNING: Could not connect to database during startup. Retrying on first request...")
    except Exception as e:
        print(f"⚠️  WARNING: Database initialization error: {e}. Retrying on first request...")


class ChatRequest(BaseModel):
    message: str

llm_client = LLMClient()
orchestrator = FinancialOrchestrator(llm_client)


@app.post("/chat-agent")
async def chat_agent(
    data: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get JWT token from cookie or header
    auth_token = None
    
    # Try to get from cookie
    auth_token = request.cookies.get("access_token")
    
    # If not in cookie, try header
    if not auth_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.replace("Bearer ", "")
    
    # Pass auth token to orchestrator for internal service calls
    result = await orchestrator.handle_request(data.message, auth_token)

    # Save FIRE result if exists
    if result.get("state", {}).get("fire_number") is not None:

        await save_fire_calculation(
            db=db,
            user_id=current_user.id,
            monthly_income=result["state"].get("monthly_income"),
            living_expense=result["state"].get("living_expense"),
            current_savings=result["state"].get("current_savings"),
            fire_number=result["state"].get("fire_number"),
            fire_year=result["state"].get("fire_year"),
            final_wealth=result["state"].get("final_wealth")
        )

    return result



@app.get("/health/db")
async def db_health(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    result = await db.execute(text("SELECT 1"))
    return {"database": "connected", "result": result.scalar()}