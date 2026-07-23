import pytest
from django.urls import reverse
from areas.models import Area


@pytest.mark.django_db
class TestAreaAPI:
    def test_list_areas_superadmin(self, admin_client, area):
        url = reverse("area-list-create")
        resp = admin_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] >= 1

    def test_list_areas_forbidden_for_user(self, auth_client):
        url = reverse("area-list-create")
        resp = auth_client.get(url)
        assert resp.status_code == 403

    def test_create_area_superadmin(self, admin_client):
        url = reverse("area-list-create")
        resp = admin_client.post(url, {
            "name": "New Zone",
            "boundary": [[23.7, 90.3], [23.8, 90.3], [23.8, 90.5]],
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["name"] == "New Zone"

    def test_create_area_forbidden_for_supervisor(self, supervisor_client):
        url = reverse("area-list-create")
        resp = supervisor_client.post(url, {
            "name": "Zone X",
            "boundary": [],
        }, format="json")
        assert resp.status_code == 403

    def test_supervisor_can_read_own_area(self, supervisor_client, area):
        url = reverse("area-detail", kwargs={"pk": area.pk})
        resp = supervisor_client.get(url)
        assert resp.status_code == 200
        assert resp.data["name"] == "Test Area"
