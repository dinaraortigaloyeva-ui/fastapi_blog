import pytest
from jose import jwt
from app.config import settings


# ─── LOGIN ────────────────────────────────────
def test_login(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# ─── TOKEN TEKSHIRISH ─────────────────────────
def test_login_token_valid(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert payload.get("user_id") == test_user["id"]


# ─── NOTO'G'RI PAROL ──────────────────────────
def test_login_wrong_password(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": "NOTO'G'RI_PAROL"
        }
    )

    assert response.status_code == 403


# ─── MAVJUD BO'LMAGAN USER ────────────────────
def test_login_wrong_email(client):
    response = client.post(
        "/login",
        data={
            "username": "yoq@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 403


# ─── TOKEN SHART ──────────────────────────────
def test_create_post_without_token(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Test post",
            "content": "Kontent"
        }
    )

    assert response.status_code == 401


# ─── REFRESH TOKEN MUVAFFAQIYATLI ──────────────
def test_refresh_token_success(client, test_user):
    login_response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ─── NOTO'G'RI REFRESH TOKEN ───────────────────
def test_refresh_token_invalid(client):
    response = client.post(
        "/refresh",
        json={"refresh_token": "noto'g'ri_token"}
    )

    assert response.status_code == 401


# ─── ACCESS TOKEN REFRESH UCHUN YAROQSIZ ───────
def test_refresh_rejects_access_token(client, test_user):
    login_response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/refresh",
        json={"refresh_token": access_token}
    )

    assert response.status_code == 401


# ─── REFRESH TOKENDA USER_ID YO'Q ──────────────
def test_refresh_token_missing_user_id(client):
    token = jwt.encode(
        {"token_type": "refresh"},
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = client.post(
        "/refresh",
        json={"refresh_token": token}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token noto'g'ri"


# ─── NOTO'G'RI USER_ID ────────────────────────
def test_refresh_token_invalid_user_id(client):
    token = jwt.encode(
        {
            "user_id": "noto'g'ri",
            "token_type": "refresh"
        },
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = client.post(
        "/refresh",
        json={"refresh_token": token}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Refresh token ichidagi user_id noto'g'ri"
    )

# ─── PARAMETRLASHTIRILGAN LOGIN TESTI ─────────
@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("test@example.com", "password123", 200),  # To'g'ri ma'lumot
        ("test@example.com", "NOTO'G'RI", 403),    # Noto'g'ri parol
        ("yoq@example.com", "password123", 403),   # Email mavjud emas
        ("test@example.com", "", 422),             # Bo'sh parol
    ],
)
def test_login_cases(client, test_user, email, password, status_code):
    response = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == status_code


# ─── FAOL BO'LMAGAN USER LOGIN QILA OLMAYDI ───
def test_login_inactive_user(client, test_user, db):
    from app import models

    user = db.query(models.User).filter(
        models.User.id == test_user["id"]
    ).first()
    user.is_active = False
    db.commit()

    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Hisobingiz faol emas"


# ─── REFRESH TOKENDA USER TOPILMAYDI ──────────
def test_refresh_token_user_not_found(client):
    token = jwt.encode(
        {
            "user_id": 99999,
            "token_type": "refresh",
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.post(
        "/refresh",
        json={"refresh_token": token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Foydalanuvchi topilmadi"


# ─── FAOL BO'LMAGAN USER REFRESH QILA OLMAYDI ─
def test_refresh_token_inactive_user(client, test_user, db):
    from app import models

    user = db.query(models.User).filter(
        models.User.id == test_user["id"]
    ).first()
    user.is_active = False
    db.commit()

    token = jwt.encode(
        {
            "user_id": test_user["id"],
            "token_type": "refresh",
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.post(
        "/refresh",
        json={"refresh_token": token},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Hisobingiz faol emas"

