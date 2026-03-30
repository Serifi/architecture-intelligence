import pytest
from fastapi import HTTPException

from backend.features.user.service import UserService
from backend.features.user.schema import UserCreate, UserUpdate, LoginPayload


class TestUserServiceListUsers:

    def test_list_users_empty(self, db_session):
        result = UserService.list_users(db_session)
        assert result == []

    def test_list_users_with_data(self, db_session, sample_user):
        result = UserService.list_users(db_session)
        assert len(result) == 1
        assert result[0].email == sample_user.email


class TestUserServiceGetUser:

    def test_get_user_success(self, db_session, sample_user):
        result = UserService.get_user(db_session, sample_user.userID)
        assert result.userID == sample_user.userID
        assert result.email == sample_user.email

    def test_get_user_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            UserService.get_user(db_session, 9999)
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail


class TestUserServiceCreateUser:

    def test_create_user_success(self, db_session):
        payload = UserCreate(
            email="newuser@example.com",
            password="securepassword123",
        )
        result = UserService.create_user(db_session, payload)
        
        assert "message" in result
        assert "user" in result
        assert result["user"].email == "newuser@example.com"

    def test_create_user_duplicate_email(self, db_session, sample_user):
        payload = UserCreate(
            email=sample_user.email,
            password="anotherpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            UserService.create_user(db_session, payload)
        assert exc_info.value.status_code == 409
        assert "email already exists" in exc_info.value.detail

    def test_create_user_email_case_insensitive(self, db_session, sample_user):
        payload = UserCreate(
            email=sample_user.email.upper(),
            password="anotherpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            UserService.create_user(db_session, payload)
        assert exc_info.value.status_code == 409


class TestUserServiceUpdateUser:

    def test_update_user_email_success(self, db_session, sample_user):
        payload = UserUpdate(email="updated@example.com")
        result = UserService.update_user(db_session, sample_user.userID, payload)
        
        assert "message" in result
        assert "user" in result
        assert result["user"].email == "updated@example.com"

    def test_update_user_password_success(self, db_session, sample_user):
        payload = UserUpdate(password="newpassword123")
        result = UserService.update_user(db_session, sample_user.userID, payload)
        
        assert "message" in result
        assert "user" in result

    def test_update_user_not_found(self, db_session):
        payload = UserUpdate(email="new@example.com")
        with pytest.raises(HTTPException) as exc_info:
            UserService.update_user(db_session, 9999, payload)
        assert exc_info.value.status_code == 404

    def test_update_user_no_fields(self, db_session, sample_user):
        payload = UserUpdate()
        with pytest.raises(HTTPException) as exc_info:
            UserService.update_user(db_session, sample_user.userID, payload)
        assert exc_info.value.status_code == 400
        assert "at least one field" in exc_info.value.detail

    def test_update_user_duplicate_email(self, db_session, sample_user, sample_user_2):
        payload = UserUpdate(email=sample_user_2.email)
        with pytest.raises(HTTPException) as exc_info:
            UserService.update_user(db_session, sample_user.userID, payload)
        assert exc_info.value.status_code == 409
        assert "email already exists" in exc_info.value.detail


class TestUserServiceLogin:

    def test_login_success(self, db_session, sample_user):
        payload = LoginPayload(
            email=sample_user.email,
            password="password123",
        )
        result = UserService.login(db_session, payload)
        
        assert "message" in result
        assert "user" in result
        assert "Login successful" in result["message"]
        assert result["user"].email == sample_user.email

    def test_login_user_not_found(self, db_session):
        payload = LoginPayload(
            email="nonexistent@example.com",
            password="anypassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            UserService.login(db_session, payload)
        assert exc_info.value.status_code == 404
        assert "User does not exist" in exc_info.value.detail

    def test_login_wrong_password(self, db_session, sample_user):
        payload = LoginPayload(
            email=sample_user.email,
            password="wrongpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            UserService.login(db_session, payload)
        assert exc_info.value.status_code == 401
        assert "Password is incorrect" in exc_info.value.detail
