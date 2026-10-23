
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .config import settings


# Token qayerdan kelishini aytamiz
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ─── ACCESS TOKEN YARATISH (30 DAQIQA) ────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
    minutes=settings.access_token_expire_minutes
)

    to_encode.update({
        "exp": expire,
        "token_type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


# ─── REFRESH TOKEN YARATISH (7 KUN) ───────────
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode.update({
        "exp": expire,
        "token_type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


# ─── ACCESS TOKENNI TEKSHIRISH ────────────────
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("user_id")
        token_type = payload.get("token_type")

        # Faqat access token qabul qilinadi
        if user_id is None or token_type != "access":
            raise credentials_exception

        token_data = schemas.TokenData(id=str(user_id))

    except JWTError:
        raise credentials_exception

    return token_data


# ─── JORIY FOYDALANUVCHINI OLISH ──────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token noto'g'ri yoki muddati tugagan",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(
        token,
        credentials_exception
    )

    try:
        user_id = int(token_data.id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisobingiz faol emas"
        )

    return user
