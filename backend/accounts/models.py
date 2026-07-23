from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with role-based access control."""

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "SuperAdmin"
        SUPERVISOR = "supervisor", "Supervisor"
        USER = "user", "User"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_user_extended"

    def __str__(self):
        return f"{self.username} ({self.role})"
