from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "report", "cleaner", "assigned_by", "assigned_at", "completed_at"]
    search_fields = ["report__title", "cleaner__user__username"]
    list_filter = ["assigned_at"]
    readonly_fields = ["assigned_at"]
