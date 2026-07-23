from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """GET /api/health/ — returns DB connectivity status."""
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "unavailable"
    return JsonResponse({"status": "ok", "database": db_status})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/reports/", include("reports.urls")),
    path("api/v1/areas/", include("areas.urls")),
    path("api/v1/cleaners/", include("cleaners.urls")),
    path("api/v1/assignments/", include("assignments.urls")),
    path("api/v1/stats/", include("stats.urls")),
    path("api/v1/users/", include("accounts.user_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
