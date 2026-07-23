from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsReporter,
    IsSuperAdmin,
    IsSupervisor,
    IsOwnerOrSupervisorOrAdmin,
)
from .models import Report
from .serializers import (
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportListSerializer,
    ReportStatusSerializer,
    AfterPhotoSerializer,
)


class UserReportListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/reports/  — list own reports (User)
    POST /api/v1/reports/  — submit new report (User)
    """
    permission_classes = [IsReporter]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReportCreateSerializer
        return ReportListSerializer

    def get_queryset(self):
        return Report.objects.filter(reporter=self.request.user).select_related(
            "area", "reporter"
        )


class ReportDetailView(generics.RetrieveAPIView):
    """GET /api/v1/reports/{id}/ — owner, supervisor, or superadmin."""
    serializer_class = ReportDetailSerializer
    permission_classes = [IsOwnerOrSupervisorOrAdmin]
    queryset = Report.objects.select_related("reporter", "area", "assignment__cleaner__user")


class AfterPhotoUploadView(APIView):
    """PATCH /api/v1/reports/{id}/after-photo/ — supervisor uploads after photo."""
    permission_classes = [IsSupervisor]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Supervisor must manage the report's area
        try:
            if report.area != request.user.managed_area:
                raise PermissionDenied
        except Exception:
            raise PermissionDenied

        serializer = AfterPhotoSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ReportDetailSerializer(report, context={"request": request}).data)


class SupervisorAreaReportsView(generics.ListAPIView):
    """GET /api/v1/reports/area/ — all reports in supervisor's area."""
    serializer_class = ReportListSerializer
    permission_classes = [IsSupervisor]

    def get_queryset(self):
        try:
            area = self.request.user.managed_area
        except Exception:
            return Report.objects.none()
        qs = Report.objects.filter(area=area).select_related("area", "reporter")

        # Optional status filter
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        # Optional search by title
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)

        return qs


class SuperAdminAllReportsView(generics.ListAPIView):
    """GET /api/v1/reports/all/ — all reports across the system (SuperAdmin)."""
    serializer_class = ReportListSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = Report.objects.select_related("area", "reporter")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs


class ReportStatusUpdateView(APIView):
    """PATCH /api/v1/reports/{id}/status/ — supervisor or superadmin changes status."""

    def get_permissions(self):
        # Allow IsSupervisor OR IsSuperAdmin
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]

    def patch(self, request, pk):
        user = request.user
        from accounts.models import User as UserModel
        if user.role not in [UserModel.Role.SUPERVISOR, UserModel.Role.SUPERADMIN]:
            return Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Supervisor scope check
        if user.role == UserModel.Role.SUPERVISOR:
            try:
                if report.area != user.managed_area:
                    return Response(
                        {"detail": "This report is not in your area."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(
                    {"detail": "You do not manage any area."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = ReportStatusSerializer(
            report, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        report.status = new_status
        if new_status == Report.Status.RESOLVED:
            report.resolved_at = timezone.now()
        report.save(update_fields=["status", "resolved_at", "updated_at"])

        # Async notification
        try:
            from reports.tasks import notify_user_status_change
            notify_user_status_change.delay(report.id, new_status)
        except Exception:
            pass

        return Response(ReportDetailSerializer(report, context={"request": request}).data)
