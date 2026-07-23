from rest_framework.permissions import BasePermission
from accounts.models import User


class IsSuperAdmin(BasePermission):
    """Only superadmin role is allowed."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.SUPERADMIN
        )


class IsSupervisor(BasePermission):
    """Only supervisor role is allowed."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.SUPERVISOR
        )


class IsReporter(BasePermission):
    """Only the regular user role is allowed to submit reports."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.USER
        )


class IsOwnerOrSupervisorOrAdmin(BasePermission):
    """
    Object-level permission:
    - Report owner can read their own report.
    - The supervisor of the area the report belongs to can access it.
    - SuperAdmin can access everything.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Role.SUPERADMIN:
            return True
        if user.role == User.Role.SUPERVISOR:
            # Check if the report belongs to the supervisor's managed area
            try:
                return obj.area == user.managed_area
            except Exception:
                return False
        # Regular user: must own the report
        return obj.reporter == user
