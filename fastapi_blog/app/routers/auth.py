
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt

from .. import models, schemas
from ..database import get_db
from ..utils.hashing import verify_password
from ..config import settings
from ..oauth2 import (
    create_access_token,
    create_refresh_token,
)


router = APIRouter(tags=["Authentication"])


# ─── TOKEN JAVOBI ─────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ─── REFRESH TOKEN SO'ROVI ────────────────────
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ─── LOGIN ────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Foydalanuvchini email orqali topish
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Noto'g'ri email yoki parol"
        )

    # Parolni tekshirish
    if not verify_password(
        user_credentials.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Noto'g'ri email yoki parol"
        )

    # Hisob faol ekanligini tekshirish
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisobingiz faol emas"
        )

    # Access va refresh token yaratish
    token_data = {"user_id": user.id}

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ─── YANGI ACCESS TOKEN OLISH ─────────────────
@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("user_id")
        token_type = payload.get("token_type")

        # Faqat refresh token qabul qilinadi
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token noto'g'ri"
            )

        # Foydalanuvchi mavjud va faol ekanligini tekshirish
        user = db.query(models.User).filter(
            models.User.id == int(user_id)
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Foydalanuvchi topilmadi"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hisobingiz faol emas"
            )

        # Yangi access token yaratish
        new_access_token = create_access_token(
            data={"user_id": user.id}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token muddati tugagan yoki noto'g'ri"
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ichidagi user_id noto'g'ri"
        )
