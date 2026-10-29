from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from cleaners.models import Cleaner
from .models import Area


class CleanerInline(admin.TabularInline):
    model = Cleaner
    extra = 0
    fields = ["user", "is_active"]
    readonly_fields = ["user"]
    show_change_link = True
    verbose_name = "Cleaner"
    verbose_name_plural = "Assigned Cleaners"


class ReportInline(admin.TabularInline):
    from reports.models import Report
    model = Report
    extra = 0
    max_num = 10
    fields = ["title", "status", "reporter", "created_at"]
    readonly_fields = ["title", "status", "reporter", "created_at"]
    show_change_link = True
    ordering = ["-created_at"]
    verbose_name = "Recent Report"
    verbose_name_plural = "Recent Reports (last 10)"
    can_delete = False

    def get_model(self):
        from reports.models import Report
        return Report

    def get_formset(self, request, obj=None, **kwargs):
        from reports.models import Report
        self.model = Report
        return super().get_formset(request, obj, **kwargs)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ["name", "supervisor_link", "cleaner_count", "report_count", "status_summary", "created_at"]
    search_fields = ["name", "supervisor__username", "supervisor__email"]
    list_per_page = 20
    readonly_fields = ["cleaner_count", "report_count", "boundary_preview"]
    inlines = [CleanerInline, ReportInline]

    fieldsets = (
        (
            "🗺️  Area Info",
            {"fields": ("name", "supervisor")},
        ),
        (
            "📐  Boundary",
            {
                "fields": ("boundary", "boundary_preview"),
                "classes": ("collapse",),
                "description": "GeoJSON-style polygon: [[lat, lng], ...]",
            },
        ),
        (
            "📊  Stats",
            {
                "fields": ("cleaner_count", "report_count"),
                "classes": ("collapse",),
            },
        ),
    )

    # ------------------------------------------------------------------
    # Custom columns
    # ------------------------------------------------------------------
    @admin.display(description="Supervisor", ordering="supervisor__username")
    def supervisor_link(self, obj):
        if not obj.supervisor:
            return format_html('<span style="color:#9ca3af;">Unassigned</span>')
        url = f"/admin/accounts/user/{obj.supervisor.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.supervisor.get_full_name() or obj.supervisor.username)

    @admin.display(description="Cleaners", ordering="cleaner_count")
    def cleaner_count(self, obj):
        count = getattr(obj, "cleaner_count", obj.cleaners.count())
        url = f"/admin/cleaners/cleaner/?area__id__exact={obj.pk}"
        return format_html('<a href="{}">{} 👷</a>', url, count)

    @admin.display(description="Reports", ordering="report_count")
    def report_count(self, obj):
        count = getattr(obj, "report_count", obj.reports.count())
        if count == 0:
            return "0"
        url = f"/admin/reports/report/?area__id__exact={obj.pk}"
        return format_html('<a href="{}" style="font-weight:600;">{} 📋</a>', url, count)

    @admin.display(description="Report Status")
    def status_summary(self, obj):
        from reports.models import Report
        qs = obj.reports.values("status").annotate(n=Count("id"))
        counts = {r["status"]: r["n"] for r in qs}
        parts = []
        badges = [
            ("pending",     "🟡", "#b45309", "#fef3c7"),
            ("in_progress", "🟠", "#c2410c", "#ffedd5"),
            ("resolved",    "🟢", "#15803d", "#dcfce7"),
        ]
        for key, icon, color, bg in badges:
            n = counts.get(key, 0)
            if n:
                parts.append(
                    f'<span style="background:{bg};color:{color};padding:1px 7px;'
                    f'border-radius:10px;font-size:11px;margin-right:3px;">{icon} {n}</span>'
                )
        return format_html("".join(parts)) if parts else "—"

    @admin.display(description="Boundary Preview")
    def boundary_preview(self, obj):
        if not obj.boundary or len(obj.boundary) < 3:
            return "No boundary defined."
        # Compute centroid
        lats = [p[0] for p in obj.boundary]
        lngs = [p[1] for p in obj.boundary]
        clat = sum(lats) / len(lats)
        clng = sum(lngs) / len(lngs)
        url = f"https://www.openstreetmap.org/#map=14/{clat}/{clng}"
        return format_html(
            '<a href="{}" target="_blank">🗺️ View centroid on OpenStreetMap</a>'
            '<br><small style="color:#6b7280;">Points: {}</small>',
            url, len(obj.boundary),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            cleaner_count=Count("cleaners", distinct=True),
            report_count=Count("reports", distinct=True),
        ).select_related("supervisor")
