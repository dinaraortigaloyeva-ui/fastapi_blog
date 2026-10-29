
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app import models
from app.config import settings
from app.oauth2 import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    get_current_user,
)


def test_create_access_token():
    token = create_access_token({"user_id": 1})
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert payload["user_id"] == 1
    assert payload["token_type"] == "access"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_create_refresh_token():
    token = create_refresh_token({"user_id": 1})
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert payload["user_id"] == 1
    assert payload["token_type"] == "refresh"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_verify_access_token_success():
    token = create_access_token({"user_id": 1})
    error = HTTPException(status_code=401)

    result = verify_access_token(token, error)

    assert result.id == "1"


def test_verify_access_token_missing_user_id():
    token = jwt.encode(
        {"token_type": "access"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    error = HTTPException(status_code=401)

    with pytest.raises(HTTPException) as exc:
        verify_access_token(token, error)

    assert exc.value.status_code == 401


def test_verify_access_token_rejects_refresh_token():
    token = create_refresh_token({"user_id": 1})
    error = HTTPException(status_code=401)

    with pytest.raises(HTTPException) as exc:
        verify_access_token(token, error)

    assert exc.value.status_code == 401


def test_verify_access_token_invalid_token():
    error = HTTPException(status_code=401)

    with pytest.raises(HTTPException) as exc:
        verify_access_token("noto'g'ri-token", error)

    assert exc.value.status_code == 401


def test_get_current_user_success(db, test_user):
    token = create_access_token({"user_id": test_user["id"]})

    user = get_current_user(token=token, db=db)

    assert user.id == test_user["id"]
    assert user.email == test_user["email"]


def test_get_current_user_missing_user(db):
    token = create_access_token({"user_id": 99999})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)

    assert exc.value.status_code == 401


def test_get_current_user_invalid_user_id(db):
    token = create_access_token({"user_id": "noto'g'ri"})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)

    assert exc.value.status_code == 401


def test_get_current_user_inactive(db, test_user):
    user = db.query(models.User).filter(
        models.User.id == test_user["id"]
    ).first()

    user.is_active = False
    db.commit()

    token = create_access_token({"user_id": test_user["id"]})

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Hisobingiz faol emas"
