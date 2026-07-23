from django.urls import path
from .views import AssignmentCreateView, AssignmentDetailView

urlpatterns = [
    path("", AssignmentCreateView.as_view(), name="assignment-create"),
    path("<int:pk>/", AssignmentDetailView.as_view(), name="assignment-detail"),
]
