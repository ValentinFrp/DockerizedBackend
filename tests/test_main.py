from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(autouse=True)
def reset_database():
    import src.main as main_module

    main_module.users_db.clear()
    main_module.user_id_counter = 1
    yield
    main_module.users_db.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123",
    }


class TestRootEndpoint:
    def test_root_returns_welcome_message(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome" in data["message"]
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestHealthCheck:
    def test_health_check_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_health_check_timestamp_format(self, client):
        response = client.get("/health")
        data = response.json()
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)


class TestCreateUser:
    def test_create_user_success(self, client, sample_user):
        response = client.post("/users", json=sample_user)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user["username"]
        assert data["email"] == sample_user["email"]
        assert data["full_name"] == sample_user["full_name"]
        assert data["id"] == 1
        assert data["is_active"] is True
        assert "created_at" in data
        assert "password" not in data

    def test_create_user_without_full_name(self, client):
        user_data = {
            "username": "minimalist",
            "email": "minimal@example.com",
            "password": "password123",
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] is None

    def test_create_user_duplicate_username(self, client, sample_user):
        client.post("/users", json=sample_user)

        duplicate_user = sample_user.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/users", json=duplicate_user)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, sample_user):
        client.post("/users", json=sample_user)

        duplicate_user = sample_user.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/users", json=duplicate_user)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_user_invalid_email(self, client):
        invalid_user = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "password123",
        }
        response = client.post("/users", json=invalid_user)
        assert response.status_code == 422  # Validation error

    def test_create_user_short_username(self, client):
        invalid_user = {
            "username": "ab",
            "email": "test@example.com",
            "password": "password123",
        }
        response = client.post("/users", json=invalid_user)
        assert response.status_code == 422

    def test_create_user_short_password(self, client):
        invalid_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",
        }
        response = client.post("/users", json=invalid_user)
        assert response.status_code == 422

    def test_create_user_missing_required_fields(self, client):
        incomplete_user = {"username": "testuser"}
        response = client.post("/users", json=incomplete_user)
        assert response.status_code == 422


class TestListUsers:
    def test_list_users_empty(self, client):
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_with_data(self, client, sample_user):
        client.post("/users", json=sample_user)

        user2 = sample_user.copy()
        user2["username"] = "user2"
        user2["email"] = "user2@example.com"
        client.post("/users", json=user2)

        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "testuser"
        assert data[1]["username"] == "user2"

    def test_list_users_pagination_skip(self, client, sample_user):
        for i in range(3):
            user = sample_user.copy()
            user["username"] = f"user{i}"
            user["email"] = f"user{i}@example.com"
            client.post("/users", json=user)

        response = client.get("/users?skip=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "user1"

    def test_list_users_pagination_limit(self, client, sample_user):
        for i in range(3):
            user = sample_user.copy()
            user["username"] = f"user{i}"
            user["email"] = f"user{i}@example.com"
            client.post("/users", json=user)

        response = client.get("/users?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetUser:
    def test_get_user_success(self, client, sample_user):
        create_response = client.post("/users", json=sample_user)
        user_id = create_response.json()["id"]

        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == sample_user["username"]

    def test_get_user_not_found(self, client):
        response = client.get("/users/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUpdateUser:
    def test_update_user_success(self, client, sample_user):
        create_response = client.post("/users", json=sample_user)
        user_id = create_response.json()["id"]

        updated_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "full_name": "Updated Name",
        }
        response = client.put(f"/users/{user_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updateduser"
        assert data["email"] == "updated@example.com"
        assert data["full_name"] == "Updated Name"
        assert data["id"] == user_id

    def test_update_user_not_found(self, client):
        updated_data = {
            "username": "newuser",
            "email": "new@example.com",
        }
        response = client.put("/users/999", json=updated_data)
        assert response.status_code == 404

    def test_update_user_duplicate_username(self, client, sample_user):
        client.post("/users", json=sample_user)

        user2 = sample_user.copy()
        user2["username"] = "user2"
        user2["email"] = "user2@example.com"
        response2 = client.post("/users", json=user2)
        user2_id = response2.json()["id"]

        updated_data = {
            "username": sample_user["username"],
            "email": "user2@example.com",
        }
        response = client.put(f"/users/{user2_id}", json=updated_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_user_duplicate_email(self, client, sample_user):
        client.post("/users", json=sample_user)

        user2 = sample_user.copy()
        user2["username"] = "user2"
        user2["email"] = "user2@example.com"
        response2 = client.post("/users", json=user2)
        user2_id = response2.json()["id"]

        updated_data = {
            "username": "user2",
            "email": sample_user["email"],
        }
        response = client.put(f"/users/{user2_id}", json=updated_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestDeleteUser:
    def test_delete_user_success(self, client, sample_user):
        create_response = client.post("/users", json=sample_user)
        user_id = create_response.json()["id"]

        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204

        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        response = client.delete("/users/999")
        assert response.status_code == 404

    def test_delete_user_removes_from_list(self, client, sample_user):
        response1 = client.post("/users", json=sample_user)
        user1_id = response1.json()["id"]

        user2 = sample_user.copy()
        user2["username"] = "user2"
        user2["email"] = "user2@example.com"
        client.post("/users", json=user2)

        client.delete(f"/users/{user1_id}")

        list_response = client.get("/users")
        data = list_response.json()
        assert len(data) == 1
        assert data[0]["username"] == "user2"


class TestIntegration:
    def test_complete_crud_workflow(self, client, sample_user):
        create_response = client.post("/users", json=sample_user)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["username"] == sample_user["username"]

        updated_data = {
            "username": "updated",
            "email": "updated@example.com",
            "full_name": "Updated User",
        }
        update_response = client.put(f"/users/{user_id}", json=updated_data)
        assert update_response.status_code == 200
        assert update_response.json()["username"] == "updated"

        list_response = client.get("/users")
        assert len(list_response.json()) == 1

        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204

        final_list = client.get("/users")
        assert len(final_list.json()) == 0

    def test_multiple_users_workflow(self, client, sample_user):
        users_to_create = 5

        created_ids = []
        for i in range(users_to_create):
            user = sample_user.copy()
            user["username"] = f"user{i}"
            user["email"] = f"user{i}@example.com"
            response = client.post("/users", json=user)
            created_ids.append(response.json()["id"])

        list_response = client.get("/users")
        assert len(list_response.json()) == users_to_create

        client.delete(f"/users/{created_ids[2]}")

        list_response = client.get("/users")
        assert len(list_response.json()) == users_to_create - 1
