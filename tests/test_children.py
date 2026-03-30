def _register_and_login(client, email, password="TestPass123!"):
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_create_child(client, auth_headers):
    res = client.post("/children/", json={
        "name": "Emma",
        "age": 5,
        "allergies": "peanuts",
        "diet_preferences": "vegetarian",
        "dislikes": "broccoli"
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Emma"
    assert res.json()["age"] == 5


def test_create_child_invalid_diet(client, auth_headers):
    res = client.post("/children/", json={
        "name": "Emma",
        "age": 5,
        "diet_preferences": "invalid-diet-type"
    }, headers=auth_headers)
    assert res.status_code == 422


def test_create_child_no_token(client):
    res = client.post("/children/", json={"name": "Emma", "age": 5})
    assert res.status_code == 401


def test_list_children(client, auth_headers):
    client.post("/children/", json={"name": "Emma", "age": 5}, headers=auth_headers)
    client.post("/children/", json={"name": "Liam", "age": 7}, headers=auth_headers)

    res = client.get("/children/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_children_excludes_other_parents(client):
    headers1 = _register_and_login(client, "parent1@test.com")
    headers2 = _register_and_login(client, "parent2@test.com")

    client.post("/children/", json={"name": "Emma", "age": 5}, headers=headers1)

    res = client.get("/children/", headers=headers2)
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_update_child(client, auth_headers):
    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=auth_headers)
    child_id = create_res.json()["id"]

    res = client.put(f"/children/{child_id}", json={"name": "Emma Updated", "age": 6}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Emma Updated"
    assert res.json()["age"] == 6


def test_update_child_not_owned(client):
    headers1 = _register_and_login(client, "owner@test.com")
    headers2 = _register_and_login(client, "other@test.com")

    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=headers1)
    child_id = create_res.json()["id"]

    res = client.put(f"/children/{child_id}", json={"name": "Hacked"}, headers=headers2)
    assert res.status_code == 404


def test_delete_child(client, auth_headers):
    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=auth_headers)
    child_id = create_res.json()["id"]

    res = client.delete(f"/children/{child_id}", headers=auth_headers)
    assert res.status_code == 204


def test_deleted_child_not_in_list(client, auth_headers):
    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=auth_headers)
    child_id = create_res.json()["id"]

    client.delete(f"/children/{child_id}", headers=auth_headers)

    res = client.get("/children/", headers=auth_headers)
    assert len(res.json()) == 0


def test_restore_child(client, auth_headers):
    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=auth_headers)
    child_id = create_res.json()["id"]

    client.delete(f"/children/{child_id}", headers=auth_headers)

    res = client.post(f"/children/{child_id}/restore", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["deleted_at"] is None

    list_res = client.get("/children/", headers=auth_headers)
    assert len(list_res.json()) == 1


def test_restore_child_not_owned(client):
    headers1 = _register_and_login(client, "restoreowner@test.com")
    headers2 = _register_and_login(client, "restoreother@test.com")

    create_res = client.post("/children/", json={"name": "Emma", "age": 5}, headers=headers1)
    child_id = create_res.json()["id"]

    client.delete(f"/children/{child_id}", headers=headers1)

    res = client.post(f"/children/{child_id}/restore", headers=headers2)
    assert res.status_code == 404
