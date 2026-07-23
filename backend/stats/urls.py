from django.urls import path
from .views import SuperAdminStatsView, SupervisorStatsView, UserStatsView

urlpatterns = [
    path("superadmin/", SuperAdminStatsView.as_view(), name="stats-superadmin"),
    path("supervisor/", SupervisorStatsView.as_view(), name="stats-supervisor"),
    path("user/", UserStatsView.as_view(), name="stats-user"),
]
