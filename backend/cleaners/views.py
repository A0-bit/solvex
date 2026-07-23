from rest_framework import generics

from accounts.permissions import IsSuperAdmin, IsSupervisor
from .models import Cleaner
from .serializers import CleanerSerializer


class CleanerListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/cleaners/  — list cleaners
    POST /api/v1/cleaners/  — add cleaner
    Supervisors see only cleaners in their area; SuperAdmins see all.
    """
    serializer_class = CleanerSerializer

    def get_permissions(self):
        return [IsSupervisor() if self.request.user.role == "supervisor" else IsSuperAdmin()]

    def get_queryset(self):
        from accounts.models import User
        user = self.request.user
        qs = Cleaner.objects.select_related("user", "area")
        if user.role == User.Role.SUPERVISOR:
            try:
                qs = qs.filter(area=user.managed_area)
            except Exception:
                return Cleaner.objects.none()
        return qs

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        from accounts.models import User
        if self.request.user.is_authenticated:
            if self.request.user.role in [User.Role.SUPERVISOR, User.Role.SUPERADMIN]:
                return [IsAuthenticated()]
        return [IsSuperAdmin()]


class CleanerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/cleaners/{id}/"""
    serializer_class = CleanerSerializer
    queryset = Cleaner.objects.select_related("user", "area")

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=["is_active"])
