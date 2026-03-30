import pytest
from fastapi import status


class TestUserEndpoints:

    def test_list_users_empty(self, client):
        response = client.get("/users/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_users_with_data(self, client, sample_user):
        response = client.get("/users/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == sample_user.email

    def test_get_user_success(self, client, sample_user):
        response = client.get(f"/users/{sample_user.userID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["userID"] == sample_user.userID
        assert data["email"] == sample_user.email

    def test_get_user_not_found(self, client):
        response = client.get("/users/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_user_success(self, client):
        payload = {
            "email": "newuser@example.com",
            "password": "securepassword123",
        }
        response = client.post("/users/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "message" in data
        assert data["user"]["email"] == "newuser@example.com"

    def test_create_user_duplicate_email(self, client, sample_user):
        payload = {
            "email": sample_user.email,
            "password": "password123",
        }
        response = client.post("/users/", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_create_user_invalid_email(self, client):
        payload = {
            "email": "invalid-email",
            "password": "password123",
        }
        response = client.post("/users/", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_user_success(self, client, sample_user):
        payload = {"email": "updated@example.com"}
        response = client.put(f"/users/{sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == "updated@example.com"

    def test_update_user_not_found(self, client):
        payload = {"email": "new@example.com"}
        response = client.put("/users/9999", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLoginEndpoint:

    def test_login_success(self, client, sample_user):
        payload = {
            "email": sample_user.email,
            "password": "password123",
        }
        response = client.post("/users/login", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Login successful" in data["message"]

    def test_login_user_not_found(self, client):
        payload = {
            "email": "nonexistent@example.com",
            "password": "anypassword",
        }
        response = client.post("/users/login", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_wrong_password(self, client, sample_user):
        payload = {
            "email": sample_user.email,
            "password": "wrongpassword",
        }
        response = client.post("/users/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
