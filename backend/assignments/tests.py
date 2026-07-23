import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from reports.models import Report
from cleaners.models import Cleaner


def make_image_file():
    img = Image.new("RGB", (10, 10))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile("img.jpg", buf.read(), content_type="image/jpeg")


@pytest.fixture
def report(db, regular_user, area):
    return Report.objects.create(
        reporter=regular_user,
        area=area,
        title="Pile",
        latitude="23.75",
        longitude="90.38",
        before_photo=SimpleUploadedFile("b.jpg", b"fake", content_type="image/jpeg"),
    )


@pytest.fixture
def cleaner(db, regular_user, area):
    return Cleaner.objects.create(user=regular_user, area=area)


@pytest.mark.django_db
class TestAssignmentCreate:
    def test_supervisor_can_assign(self, supervisor_client, supervisor_user, area, report, cleaner):
        area.supervisor = supervisor_user
        area.save()
        url = reverse("assignment-create")
        resp = supervisor_client.post(url, {
            "report": report.id,
            "cleaner": cleaner.id,
            "notes": "Please handle ASAP",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["notes"] == "Please handle ASAP"

    def test_assignment_auto_transitions_report_to_assigned(
        self, supervisor_client, supervisor_user, area, report, cleaner
    ):
        area.supervisor = supervisor_user
        area.save()
        url = reverse("assignment-create")
        supervisor_client.post(url, {
            "report": report.id,
            "cleaner": cleaner.id,
        }, format="json")
        report.refresh_from_db()
        assert report.status == Report.Status.ASSIGNED

    def test_user_cannot_assign(self, auth_client, report, cleaner):
        url = reverse("assignment-create")
        resp = auth_client.post(url, {
            "report": report.id,
            "cleaner": cleaner.id,
        }, format="json")
        assert resp.status_code == 403
