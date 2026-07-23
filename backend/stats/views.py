from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsSuperAdmin, IsSupervisor, IsReporter
from reports.models import Report


class SuperAdminStatsView(APIView):
    """GET /api/v1/stats/superadmin/ — system-wide dashboard counts."""
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        status_counts = (
            Report.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        return Response(
            {
                "total_reports": Report.objects.count(),
                "reports_by_status": {
                    item["status"]: item["count"] for item in status_counts
                },
                "total_users": User.objects.filter(role=User.Role.USER).count(),
                "total_supervisors": User.objects.filter(role=User.Role.SUPERVISOR).count(),
                "total_areas": __import__(
                    "areas.models", fromlist=["Area"]
                ).Area.objects.count(),
                "total_cleaners": __import__(
                    "cleaners.models", fromlist=["Cleaner"]
                ).Cleaner.objects.filter(is_active=True).count(),
            }
        )


class SupervisorStatsView(APIView):
    """GET /api/v1/stats/supervisor/ — area-scoped counts."""
    permission_classes = [IsSupervisor]

    def get(self, request):
        try:
            area = request.user.managed_area
        except Exception:
            return Response({"detail": "You do not manage any area."}, status=400)

        area_reports = Report.objects.filter(area=area)
        status_counts = (
            area_reports.values("status").annotate(count=Count("id")).order_by("status")
        )
        return Response(
            {
                "area": area.name,
                "total_reports": area_reports.count(),
                "reports_by_status": {
                    item["status"]: item["count"] for item in status_counts
                },
                "active_cleaners": __import__(
                    "cleaners.models", fromlist=["Cleaner"]
                ).Cleaner.objects.filter(area=area, is_active=True).count(),
            }
        )


class UserStatsView(APIView):
    """GET /api/v1/stats/user/ — own report counts."""
    permission_classes = [IsReporter]

    def get(self, request):
        my_reports = Report.objects.filter(reporter=request.user)
        status_counts = (
            my_reports.values("status").annotate(count=Count("id")).order_by("status")
        )
        return Response(
            {
                "total_reports": my_reports.count(),
                "reports_by_status": {
                    item["status"]: item["count"] for item in status_counts
                },
                "recent_reports": list(
                    my_reports.values(
                        "id", "title", "status", "created_at"
                    ).order_by("-created_at")[:3]
                ),
            }
        )
