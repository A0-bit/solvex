from django.db import models


class Assignment(models.Model):
    """Links a report to a cleaner, created by a supervisor."""

    report = models.OneToOneField(
        "reports.Report",
        on_delete=models.CASCADE,
        related_name="assignment",
    )
    cleaner = models.ForeignKey(
        "cleaners.Cleaner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments",
    )
    assigned_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments_made",
    )
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Assignment for Report #{self.report_id}"
