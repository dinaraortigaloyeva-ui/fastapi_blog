import pytest
from jose import jwt
from app.config import settings

# ─── FOYDALANUVCHI YARATISH ───────────────────
def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "ali@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "ali@example.com"
    assert data["username"] == "ali"
    assert "password" not in data    # Parol ko'rinmasin!
    assert "id" in data
    assert "created_at" in data

# ─── TAKRORIY EMAIL ───────────────────────────
def test_create_user_duplicate_email(client):
    # Birinchi user
    client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "ali@example.com",
            "password": "password123"
        }
    )

    # Xuddi shu email bilan yana
    response = client.post(
        "/users/",
        json={
            "username": "vali",
            "email": "ali@example.com",   # Takror!
            "password": "password456"
        }
    )
    assert response.status_code == 400
    assert "allaqachon" in response.json()["detail"]

# ─── NOTO'G'RI MA'LUMOT ───────────────────────
def test_create_user_invalid_email(client):
    response = client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "bu-email-emas",    # Noto'g'ri email
            "password": "password123"
        }
    )
    assert response.status_code == 422   # Validation error

# ─── FOYDALANUVCHINI OLISH ────────────────────
def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]

# ─── MAVJUD BO'LMAGAN USER ────────────────────
def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_get_current_user(authorized_client, test_user):
    response = authorized_client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]


def test_get_current_user_unauthorized(client):
    response = client.get("/users/me")

    assert response.status_code == 401

def test_change_password(authorized_client, test_user):
    response = authorized_client.put(
        "/users/me/password",
        json={
            "old_password": test_user["password"],
            "new_password": "yangi_parol_123"
        }
    )

    assert response.status_code == 200

def test_change_password_and_login(authorized_client, client, test_user):
    response = authorized_client.put(
        "/users/me/password",
        json={
            "old_password": test_user["password"],
            "new_password": "yangi_parol_123"
        }
    )

    assert response.status_code == 200

    # Eski parol bilan login ishlamasligi kerak
    old_password_response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert old_password_response.status_code == 403

    # Yangi parol bilan login ishlashi kerak
    new_password_response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": "yangi_parol_123"
        }
    )
    assert new_password_response.status_code == 200

# ─── ESKI PAROL NOTO'G'RI ─────────────────────
def test_change_password_wrong_old_password(authorized_client):
    response = authorized_client.put(
        "/users/me/password",
        json={
            "old_password": "wrong_password",
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Eski parol noto'g'ri"


# ─── USERS ROUTERIDAGI POSTLAR RO'YXATI ───────
def test_get_posts_from_users_router(client, test_posts):
    response = client.get("/users/")

    assert response.status_code == 200
    assert len(response.json()) == len(test_posts)
