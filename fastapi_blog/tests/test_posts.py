
from app import models
from app.utils.hashing import hash_password


# ─── BARCHA POSTLAR ───────────────────────────
def test_get_all_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(test_posts)


# ─── BITTA POST ───────────────────────────────
def test_get_post(client, test_posts):
    post_id = test_posts[0].id

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == test_posts[0].title


# ─── MAVJUD BO'LMAGAN POSTNI OLISH ────────────
def test_get_post_not_found(client):
    response = client.get("/posts/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "ID=99999 bo'lgan post topilmadi"
    )


# ─── POST YARATISH (TOKEN BILAN) ──────────────
def test_create_post(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={
            "title": "Yangi post",
            "body": "Yangi kontent",
            "published": True,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Yangi post"
    assert data["body"] == "Yangi kontent"
    assert data["published"] is True
    assert "id" in data
    assert "owner_id" in data


# ─── POST YARATISH (TOKEN YO'Q) ───────────────
def test_create_post_unauthorized(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Post",
            "body": "Kontent",
        },
    )

    assert response.status_code == 401


# ─── DEFAULT PUBLISHED = TRUE ─────────────────
def test_create_post_default_published(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={
            "title": "Post",
            "body": "Kontent",
        },
    )

    assert response.status_code == 201
    assert response.json()["published"] is True


# ─── POST YANGILASH ───────────────────────────
def test_update_post(authorized_client, test_posts):
    post_id = test_posts[0].id

    response = authorized_client.put(
        f"/posts/{post_id}",
        json={
            "title": "Yangilangan sarlavha",
            "body": "Yangilangan kontent",
            "published": True,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Yangilangan sarlavha"
    assert data["body"] == "Yangilangan kontent"


# ─── MAVJUD BO'LMAGAN POSTNI YANGILASH ────────
def test_update_post_not_found(authorized_client):
    response = authorized_client.put(
        "/posts/99999",
        json={
            "title": "Yangi sarlavha",
            "body": "Yangi matn",
            "published": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "ID=99999 bo'lgan post topilmadi"
    )


# ─── BOSHQANING POSTINI YANGILASH ─────────────
def test_update_other_user_post(authorized_client, db):
    other_user = models.User(
        username="other",
        email="other@example.com",
        password=hash_password("password123"),
    )

    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    other_post = models.Post(
        title="Boshqaning posti",
        body="Kontent",
        owner_id=other_user.id,
    )

    db.add(other_post)
    db.commit()
    db.refresh(other_post)

    response = authorized_client.put(
        f"/posts/{other_post.id}",
        json={
            "title": "O'zgartirishga urinish",
            "body": "Kontent",
            "published": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Siz bu postni yangilay olmaysiz"
    )


# ─── POST O'CHIRISH ───────────────────────────
def test_delete_post(authorized_client, test_posts):
    post_id = test_posts[0].id

    response = authorized_client.delete(
        f"/posts/{post_id}"
    )

    assert response.status_code == 204


# ─── O'CHIRILGAN POSTNI TEKSHIRISH ────────────
def test_delete_post_check(authorized_client, test_posts):
    post_id = test_posts[0].id

    delete_response = authorized_client.delete(
        f"/posts/{post_id}"
    )

    assert delete_response.status_code == 204

    response = authorized_client.get(
        f"/posts/{post_id}"
    )

    assert response.status_code == 404


# ─── MAVJUD BO'LMAGAN POSTNI O'CHIRISH ────────
def test_delete_post_not_found(authorized_client):
    response = authorized_client.delete("/posts/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "ID=99999 bo'lgan post topilmadi"
    )


# ─── BOSHQANING POSTINI O'CHIRISH ─────────────
def test_delete_other_user_post(authorized_client, db):
    other_user = models.User(
        username="other2",
        email="other2@example.com",
        password=hash_password("password123"),
    )

    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    other_post = models.Post(
        title="Boshqaning posti",
        body="Kontent",
        owner_id=other_user.id,
    )

    db.add(other_post)
    db.commit()
    db.refresh(other_post)

    response = authorized_client.delete(
        f"/posts/{other_post.id}"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Siz bu postni o'chira olmaysiz"
    )


# ─── PAGINATION ───────────────────────────────
def test_get_posts_pagination(client, test_posts):
    response = client.get("/posts/?limit=2&skip=0")

    assert response.status_code == 200
    assert len(response.json()) == 2

    response2 = client.get("/posts/?limit=2&skip=2")

    assert response2.status_code == 200
    assert len(response2.json()) == 1


# ─── QIDIRUV ──────────────────────────────────
def test_get_posts_search(client, test_posts):
    response = client.get("/posts/?search=Birinchi")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Birinchi post"


# ─── NATIJA TOPILMAYDIGAN QIDIRUV ─────────────
def test_get_posts_search_no_results(client, test_posts):
    response = client.get("/posts/?search=BuNomMavjudEmas")

    assert response.status_code == 200
    assert response.json() == []

