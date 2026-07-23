from django.urls import path
from .views import CleanerListCreateView, CleanerDetailView

urlpatterns = [
    path("", CleanerListCreateView.as_view(), name="cleaner-list-create"),
    path("<int:pk>/", CleanerDetailView.as_view(), name="cleaner-detail"),
]
