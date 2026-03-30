def test_register_success(client):
    res = client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "TestPass123!"
    })
    assert res.status_code == 200
    assert res.json()["email"] == "newuser@test.com"
    assert res.json()["is_email_verified"] == False


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "TestPass123!"})
    res = client.post("/auth/register", json={"email": "dup@test.com", "password": "TestPass123!"})
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


def test_register_weak_password(client):
    res = client.post("/auth/register", json={
        "email": "weak@test.com",
        "password": "password"
    })
    assert res.status_code == 422


def test_login_success(client, registered_user):
    res = client.post("/auth/login", json=registered_user)
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert "refresh_token" in res.json()


def test_login_wrong_password(client, registered_user):
    res = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": "WrongPass999!"
    })
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/auth/login", json={
        "email": "nobody@test.com",
        "password": "TestPass123!"
    })
    assert res.status_code == 401


def test_refresh_token(client, registered_user):
    login_res = client.post("/auth/login", json=registered_user)
    refresh_token = login_res.json()["refresh_token"]

    res = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_refresh_token_invalid(client):
    res = client.post("/auth/refresh", json={"refresh_token": "fake.token.here"})
    assert res.status_code == 401


def test_verify_email(client, db_session):
    from app.models.user import User

    client.post("/auth/register", json={"email": "verify@test.com", "password": "TestPass123!"})
    user = db_session.query(User).filter(User.email == "verify@test.com").first()
    token = user.email_verification_token

    res = client.post("/auth/verify-email", json={"token": token})
    assert res.status_code == 200
    assert res.json()["message"] == "Email verified successfully"


def test_verify_email_invalid_token(client):
    res = client.post("/auth/verify-email", json={"token": "fake-token"})
    assert res.status_code == 400


def test_forgot_password(client, registered_user):
    res = client.post("/auth/forgot-password", json={"email": registered_user["email"]})
    assert res.status_code == 200


def test_reset_password(client, db_session, registered_user):
    from app.models.user import User

    client.post("/auth/forgot-password", json={"email": registered_user["email"]})

    db_session.expire_all()
    user = db_session.query(User).filter(User.email == registered_user["email"]).first()

    res = client.post("/auth/reset-password", json={
        "token": user.password_reset_token,
        "new_password": "NewPass456!"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "Password reset successfully"


def test_reset_password_invalid_token(client):
    res = client.post("/auth/reset-password", json={
        "token": "fake-token",
        "new_password": "NewPass456!"
    })
    assert res.status_code == 400


def test_get_me(client, auth_headers, registered_user):
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == registered_user["email"]


def test_get_me_no_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 401
