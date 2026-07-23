import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from reports.models import Report


def make_image_file(name="test.jpg"):
    """Create a minimal valid JPEG in memory."""
    img = Image.new("RGB", (50, 50), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/jpeg")


@pytest.fixture
def report(db, regular_user, area):
    return Report.objects.create(
        reporter=regular_user,
        area=area,
        title="Test garbage pile",
        description="Big pile near the road",
        latitude="23.7500",
        longitude="90.3750",
        before_photo=SimpleUploadedFile("before.jpg", b"fake", content_type="image/jpeg"),
    )


@pytest.mark.django_db
class TestReportCreate:
    def test_user_can_create_report(self, auth_client, regular_user):
        url = reverse("report-list-create")
        resp = auth_client.post(url, {
            "title": "Garbage near park",
            "description": "Overflow",
            "latitude": "23.7400",
            "longitude": "90.3600",
            "before_photo": make_image_file(),
        }, format="multipart")
        assert resp.status_code == 201
        assert resp.data["title"] == "Garbage near park"
        assert resp.data["status"] == "pending"

    def test_supervisor_cannot_create_report(self, supervisor_client):
        url = reverse("report-list-create")
        resp = supervisor_client.post(url, {
            "title": "X",
            "latitude": "23.74",
            "longitude": "90.36",
            "before_photo": make_image_file(),
        }, format="multipart")
        assert resp.status_code == 403

    def test_unauthenticated_cannot_create(self, api_client):
        url = reverse("report-list-create")
        resp = api_client.post(url, {
            "title": "X",
            "latitude": "23.74",
            "longitude": "90.36",
            "before_photo": make_image_file(),
        }, format="multipart")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestReportList:
    def test_user_sees_only_own_reports(self, auth_client, regular_user, report, db):
        from accounts.models import User
        other = User.objects.create_user(username="other", email="o@t.com", password="p", role="user")
        Report.objects.create(
            reporter=other, title="Other", latitude="23.74", longitude="90.36",
            before_photo=SimpleUploadedFile("x.jpg", b"x", content_type="image/jpeg"),
        )
        url = reverse("report-list-create")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        for r in resp.data["results"]:
            assert r["reporter_name"] != "other"

    def test_supervisor_sees_area_reports(self, supervisor_client, report):
        url = reverse("report-area-list")
        resp = supervisor_client.get(url)
        assert resp.status_code == 200


@pytest.mark.django_db
class TestReportStatusUpdate:
    def test_supervisor_can_reject_pending_report(self, supervisor_client, supervisor_user, area, report):
        # Supervisor must manage the area
        area.supervisor = supervisor_user
        area.save()
        url = reverse("report-status-update", kwargs={"pk": report.pk})
        resp = supervisor_client.patch(url, {"status": "rejected"}, format="json")
        assert resp.status_code == 200
        assert resp.data["status"] == "rejected"

    def test_cannot_resolve_without_after_photo(self, supervisor_client, supervisor_user, area, report):
        area.supervisor = supervisor_user
        area.save()
        report.status = Report.Status.IN_PROGRESS
        report.save()
        url = reverse("report-status-update", kwargs={"pk": report.pk})
        resp = supervisor_client.patch(url, {"status": "resolved"}, format="json")
        assert resp.status_code == 400

    def test_invalid_transition_rejected(self, supervisor_client, supervisor_user, area, report):
        area.supervisor = supervisor_user
        area.save()
        # Cannot go pending → resolved directly
        url = reverse("report-status-update", kwargs={"pk": report.pk})
        resp = supervisor_client.patch(url, {"status": "resolved"}, format="json")
        assert resp.status_code == 400
