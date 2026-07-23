from django.urls import path
from .views import (
    UserReportListCreateView,
    ReportDetailView,
    AfterPhotoUploadView,
    SupervisorAreaReportsView,
    SuperAdminAllReportsView,
    ReportStatusUpdateView,
)

urlpatterns = [
    path("", UserReportListCreateView.as_view(), name="report-list-create"),
    path("area/", SupervisorAreaReportsView.as_view(), name="report-area-list"),
    path("all/", SuperAdminAllReportsView.as_view(), name="report-all-list"),
    path("<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("<int:pk>/after-photo/", AfterPhotoUploadView.as_view(), name="report-after-photo"),
    path("<int:pk>/status/", ReportStatusUpdateView.as_view(), name="report-status-update"),
]
