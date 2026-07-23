import io
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from areas.serializers import AreaSerializer
from .models import Report
from .utils import resolve_area, strip_exif


def _validate_image_field(value, max_mb: int = 10):
    """Shared image validator: extension + size + EXIF strip."""
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]
    ext = value.name.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise serializers.ValidationError(
            f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}."
        )
    if value.size > max_mb * 1024 * 1024:
        raise serializers.ValidationError(f"Image must be under {max_mb} MB.")

    # Strip EXIF
    cleaned_bytes = strip_exif(value)
    return ContentFile(cleaned_bytes, name=f"photo.{ext}")


class AssignmentInlineSerializer(serializers.Serializer):
    """Minimal read-only representation of an assignment for nesting."""
    id = serializers.IntegerField()
    cleaner_id = serializers.IntegerField(source="cleaner.id", allow_null=True)
    cleaner_name = serializers.SerializerMethodField()
    notes = serializers.CharField()
    assigned_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)

    def get_cleaner_name(self, obj):
        if obj.cleaner and obj.cleaner.user:
            return obj.cleaner.user.get_full_name() or obj.cleaner.user.username
        return None


class ReportCreateSerializer(serializers.ModelSerializer):
    before_photo = serializers.ImageField(
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])]
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "description",
            "latitude",
            "longitude",
            "before_photo",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_before_photo(self, value):
        return _validate_image_field(value, max_mb=10)

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["reporter"] = request.user

        # Auto-assign area based on coordinates
        lat = validated_data.get("latitude")
        lng = validated_data.get("longitude")
        validated_data["area"] = resolve_area(lat, lng)

        report = Report.objects.create(**validated_data)

        # Trigger async notification (fire-and-forget)
        try:
            from reports.tasks import notify_supervisor_new_report
            notify_supervisor_new_report.delay(report.id)
        except Exception:
            pass

        return report


class ReportDetailSerializer(serializers.ModelSerializer):
    reporter = UserProfileSerializer(read_only=True)
    area = AreaSerializer(read_only=True)
    assignment = AssignmentInlineSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "area",
            "title",
            "description",
            "latitude",
            "longitude",
            "before_photo",
            "after_photo",
            "status",
            "assignment",
            "created_at",
            "updated_at",
            "resolved_at",
        ]


class ReportStatusSerializer(serializers.ModelSerializer):
    """Used by supervisor/admin to change report status."""

    class Meta:
        model = Report
        fields = ["status"]

    def validate_status(self, new_status):
        report = self.instance
        current = report.status

        # State machine: valid transitions
        valid_transitions = {
            Report.Status.PENDING: [Report.Status.REJECTED],
            Report.Status.ASSIGNED: [Report.Status.IN_PROGRESS, Report.Status.REJECTED],
            Report.Status.IN_PROGRESS: [Report.Status.RESOLVED, Report.Status.REJECTED],
            Report.Status.RESOLVED: [],
            Report.Status.REJECTED: [],  # SuperAdmin can re-open (handled separately)
        }

        # SuperAdmin can re-open rejected reports
        request = self.context.get("request")
        if (
            request
            and hasattr(request.user, "role")
            and request.user.role == "superadmin"
            and current == Report.Status.REJECTED
            and new_status == Report.Status.PENDING
        ):
            return new_status

        if new_status not in valid_transitions.get(current, []):
            raise serializers.ValidationError(
                f"Cannot transition from '{current}' to '{new_status}'."
            )

        # RESOLVED requires after_photo
        if new_status == Report.Status.RESOLVED and not report.after_photo:
            raise serializers.ValidationError(
                "After photo required before resolving this report."
            )

        return new_status


class AfterPhotoSerializer(serializers.ModelSerializer):
    after_photo = serializers.ImageField(
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])]
    )

    class Meta:
        model = Report
        fields = ["after_photo"]

    def validate_after_photo(self, value):
        return _validate_image_field(value, max_mb=10)


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    reporter_name = serializers.SerializerMethodField()
    area_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "status",
            "reporter_name",
            "area_name",
            "latitude",
            "longitude",
            "before_photo",
            "created_at",
        ]

    def get_reporter_name(self, obj):
        return obj.reporter.get_full_name() or obj.reporter.username

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None
