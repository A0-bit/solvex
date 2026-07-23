import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRegister:
    def test_register_creates_user(self, api_client):
        url = reverse("auth-register")
        resp = api_client.post(url, {
            "username": "newuser",
            "email": "new@test.com",
            "password": "strongpass1",
            "password2": "strongpass1",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["username"] == "newuser"
        assert resp.data["role"] == "user"

    def test_register_password_mismatch(self, api_client):
        url = reverse("auth-register")
        resp = api_client.post(url, {
            "username": "newuser2",
            "email": "new2@test.com",
            "password": "pass1",
            "password2": "pass2",
        }, format="json")
        assert resp.status_code == 400

    def test_register_cannot_self_assign_superadmin(self, api_client):
        url = reverse("auth-register")
        resp = api_client.post(url, {
            "username": "hacker",
            "email": "hacker@test.com",
            "password": "strongpass1",
            "password2": "strongpass1",
            "role": "superadmin",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["role"] == "user"


@pytest.mark.django_db
class TestLogin:
    def test_login_returns_tokens(self, api_client, regular_user):
        url = reverse("auth-login")
        resp = api_client.post(url, {
            "username": "testuser",
            "password": "testpass123",
        }, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data
        assert resp.data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, api_client, regular_user):
        url = reverse("auth-login")
        resp = api_client.post(url, {
            "username": "testuser",
            "password": "wrongpass",
        }, format="json")
        assert resp.status_code == 400

    def test_login_inactive_user(self, api_client, regular_user):
        regular_user.is_active = False
        regular_user.save()
        url = reverse("auth-login")
        resp = api_client.post(url, {
            "username": "testuser",
            "password": "testpass123",
        }, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestMe:
    def test_get_me(self, auth_client):
        url = reverse("auth-me")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["username"] == "testuser"

    def test_me_unauthenticated(self, api_client):
        url = reverse("auth-me")
        resp = api_client.get(url)
        assert resp.status_code == 401

    def test_update_me(self, auth_client):
        url = reverse("auth-me")
        resp = auth_client.patch(url, {"first_name": "John"}, format="json")
        assert resp.status_code == 200
        assert resp.data["first_name"] == "John"
