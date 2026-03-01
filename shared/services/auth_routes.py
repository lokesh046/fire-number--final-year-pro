from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database import get_db
from shared.models.user import User
from shared.services.auth import create_access_token, verify_password, hash_password

from pydantic import BaseModel, EmailStr

router = APIRouter()


# -------------------------
# Register
# -------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="user",
        is_active=True,
        is_verified=True,
    )

    db.add(new_user)
    await db.commit()

    return {"message": "User created successfully", "email": data.email}


# -------------------------
# Login (OAuth2 Compatible) - With Cookie
# -------------------------

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Set cookie for automatic token handling
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=3600 * 24 * 7  # 7 days
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "message": "Login successful! Token saved in cookie."
    }


# -------------------------
# Logout
# -------------------------

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}
