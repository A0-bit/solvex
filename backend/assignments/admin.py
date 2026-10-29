from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Assignment


@admin.action(description="✅  Mark selected assignments as completed")
def mark_completed(modeladmin, request, queryset):
    queryset.filter(completed_at__isnull=True).update(completed_at=timezone.now())


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "report_link",
        "cleaner_link",
        "assigned_by_link",
        "report_status_badge",
        "duration_display",
        "assigned_at",
        "completed_at",
    ]
    search_fields = ["report__title", "cleaner__user__username", "assigned_by__username"]
    list_filter = ["assigned_at", "completed_at"]
    readonly_fields = ["assigned_at", "assigned_by", "report_status_badge"]
    ordering = ["-assigned_at"]
    list_per_page = 25
    actions = [mark_completed]

    fieldsets = (
        (
            "📋  Assignment Details",
            {
                "fields": (
                    "report",
                    "report_status_badge",
                    "cleaner",
                    "assigned_by",
                    "notes",
                )
            },
        ),
        (
            "🕒  Timestamps",
            {
                "fields": ("assigned_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # ------------------------------------------------------------------
    # Custom columns
    # ------------------------------------------------------------------
    @admin.display(description="Report", ordering="report__title")
    def report_link(self, obj):
        url = f"/admin/reports/report/{obj.report.pk}/change/"
        return format_html('<a href="{}">#{} — {}</a>', url, obj.report.pk, obj.report.title[:40])

    @admin.display(description="Cleaner", ordering="cleaner__user__username")
    def cleaner_link(self, obj):
        if not obj.cleaner:
            return format_html('<span style="color:#9ca3af;">—</span>')
        url = f"/admin/cleaners/cleaner/{obj.cleaner.pk}/change/"
        name = obj.cleaner.user.get_full_name() or obj.cleaner.user.username
        return format_html('<a href="{}">{}</a>', url, name)

    @admin.display(description="Assigned by", ordering="assigned_by__username")
    def assigned_by_link(self, obj):
        if not obj.assigned_by:
            return "—"
        url = f"/admin/accounts/user/{obj.assigned_by.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.assigned_by.username)

    @admin.display(description="Report Status")
    def report_status_badge(self, obj):
        colours = {
            "pending":     ("#b45309", "#fef3c7"),
            "assigned":    ("#1d4ed8", "#dbeafe"),
            "in_progress": ("#c2410c", "#ffedd5"),
            "resolved":    ("#15803d", "#dcfce7"),
            "rejected":    ("#b91c1c", "#fee2e2"),
        }
        status = obj.report.status
        color, bg = colours.get(status, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:12px;'
            'font-size:11px;font-weight:700;">{}</span>',
            bg, color, status.replace("_", " ").title(),
        )

    @admin.display(description="Duration")
    def duration_display(self, obj):
        if obj.completed_at:
            delta = obj.completed_at - obj.assigned_at
            hours = int(delta.total_seconds() // 3600)
            return format_html(
                '<span style="color:#15803d;font-weight:600;">{}h ✓</span>', hours
            )
        delta = timezone.now() - obj.assigned_at
        hours = int(delta.total_seconds() // 3600)
        color = "#b91c1c" if hours > 48 else "#b45309" if hours > 24 else "#374151"
        return format_html('<span style="color:{};">{}h open</span>', color, hours)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "report", "cleaner__user", "assigned_by"
        )
