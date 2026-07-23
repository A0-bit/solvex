from rest_framework import generics, status
from rest_framework.response import Response

from accounts.permissions import IsSuperAdmin, IsSupervisor
from reports.models import Report
from .models import Assignment
from .serializers import AssignmentSerializer


class AssignmentCreateView(generics.CreateAPIView):
    """POST /api/v1/assignments/ — assign a cleaner to a report (Supervisor)."""
    serializer_class = AssignmentSerializer
    permission_classes = [IsSupervisor]

    def perform_create(self, serializer):
        assignment = serializer.save(assigned_by=self.request.user)

        # Auto-transition report status to ASSIGNED (Task 13.3)
        report = assignment.report
        if report.status == Report.Status.PENDING:
            report.status = Report.Status.ASSIGNED
            report.save(update_fields=["status", "updated_at"])

            # Notify user
            try:
                from reports.tasks import notify_user_status_change
                notify_user_status_change.delay(report.id, Report.Status.ASSIGNED)
            except Exception:
                pass


class AssignmentDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/assignments/{id}/"""
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.select_related(
        "report", "cleaner__user", "assigned_by"
    )

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]
