from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSuperAdmin, IsSupervisor
from .models import Area
from .serializers import AreaSerializer


class AreaListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/areas/  — list areas (SuperAdmin)
    POST /api/v1/areas/  — create area (SuperAdmin)
    """
    serializer_class = AreaSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Area.objects.select_related("supervisor").all()


class AreaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/areas/{id}/  — SuperAdmin or Supervisor
    PATCH  /api/v1/areas/{id}/  — SuperAdmin only
    DELETE /api/v1/areas/{id}/  — SuperAdmin only
    """
    serializer_class = AreaSerializer
    queryset = Area.objects.select_related("supervisor").all()

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [IsSuperAdmin()]
        return [IsAuthenticated()]
