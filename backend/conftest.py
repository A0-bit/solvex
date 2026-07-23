import django
import os
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def superadmin_user(db):
    from accounts.models import User
    return User.objects.create_superuser(
        username="superadmin",
        email="superadmin@test.com",
        password="testpass123",
        role="superadmin",
    )


@pytest.fixture
def supervisor_user(db):
    from accounts.models import User
    return User.objects.create_user(
        username="supervisor",
        email="supervisor@test.com",
        password="testpass123",
        role="supervisor",
    )


@pytest.fixture
def regular_user(db):
    from accounts.models import User
    return User.objects.create_user(
        username="testuser",
        email="user@test.com",
        password="testpass123",
        role="user",
    )


@pytest.fixture
def auth_client(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def supervisor_client(api_client, supervisor_user):
    api_client.force_authenticate(user=supervisor_user)
    return api_client


@pytest.fixture
def admin_client(api_client, superadmin_user):
    api_client.force_authenticate(user=superadmin_user)
    return api_client


@pytest.fixture
def area(db, supervisor_user):
    from areas.models import Area
    return Area.objects.create(
        name="Test Area",
        supervisor=supervisor_user,
        boundary=[[23.7, 90.3], [23.8, 90.3], [23.8, 90.5], [23.7, 90.5]],
    )
