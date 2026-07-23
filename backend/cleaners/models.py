from django.db import models


class Cleaner(models.Model):
    """A field worker managed by a supervisor."""

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cleaner_profile",
    )
    area = models.ForeignKey(
        "areas.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cleaners",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.area}"
