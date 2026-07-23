from rest_framework import serializers
from .models import Assignment
from reports.serializers import ReportListSerializer
from cleaners.serializers import CleanerSerializer
from accounts.serializers import UserProfileSerializer


class AssignmentSerializer(serializers.ModelSerializer):
    report_detail = ReportListSerializer(source="report", read_only=True)
    cleaner_detail = CleanerSerializer(source="cleaner", read_only=True)
    assigned_by_detail = UserProfileSerializer(source="assigned_by", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "report",
            "report_detail",
            "cleaner",
            "cleaner_detail",
            "assigned_by",
            "assigned_by_detail",
            "notes",
            "assigned_at",
            "completed_at",
        ]
        read_only_fields = ["assigned_by", "assigned_at"]
