from django.db import models


class Area(models.Model):
    """Geographic zone managed by one supervisor."""

    name = models.CharField(max_length=200)
    # Boundary polygon stored as [[lat, lng], ...] JSON array
    boundary = models.JSONField(default=list)
    supervisor = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_area",
        limit_choices_to={"role": "supervisor"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
