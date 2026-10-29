import csv
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Report


# ---------------------------------------------------------------------------
# Inline: show the assignment right inside the report change page
# ---------------------------------------------------------------------------
class AssignmentInline(admin.StackedInline):
    from assignments.models import Assignment
    model = Assignment
    extra = 0
    can_delete = False
    readonly_fields = ["assigned_by", "assigned_at", "completed_at"]
    fields = ["cleaner", "notes", "assigned_by", "assigned_at", "completed_at"]
    verbose_name = "Assignment"
    verbose_name_plural = "Assignment"
    show_change_link = True

    def get_model(self):
        from assignments.models import Assignment
        return Assignment

    def get_formset(self, request, obj=None, **kwargs):
        from assignments.models import Assignment
        self.model = Assignment
        return super().get_formset(request, obj, **kwargs)


# ---------------------------------------------------------------------------
# Custom bulk actions
# ---------------------------------------------------------------------------
@admin.action(description="✅  Mark selected reports as Resolved")
def mark_resolved(modeladmin, request, queryset):
    updated = queryset.exclude(status=Report.Status.RESOLVED).update(
        status=Report.Status.RESOLVED,
        resolved_at=timezone.now(),
    )
    modeladmin.message_user(request, f"{updated} report(s) marked as resolved.", messages.SUCCESS)


@admin.action(description="🚫  Mark selected reports as Rejected")
def mark_rejected(modeladmin, request, queryset):
    updated = queryset.exclude(status=Report.Status.REJECTED).update(
        status=Report.Status.REJECTED,
    )
    modeladmin.message_user(request, f"{updated} report(s) marked as rejected.", messages.WARNING)


@admin.action(description="🔄  Reset selected reports to Pending")
def reset_pending(modeladmin, request, queryset):
    updated = queryset.update(
        status=Report.Status.PENDING,
        resolved_at=None,
    )
    modeladmin.message_user(request, f"{updated} report(s) reset to pending.", messages.INFO)


@admin.action(description="📥  Export selected reports to CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reports.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "ID", "Title", "Status", "Reporter", "Area",
        "Latitude", "Longitude", "Created At", "Resolved At",
    ])
    for r in queryset.select_related("reporter", "area"):
        writer.writerow([
            r.id, r.title, r.status,
            r.reporter.username if r.reporter else "",
            r.area.name if r.area else "",
            r.latitude, r.longitude,
            r.created_at.strftime("%Y-%m-%d %H:%M"),
            r.resolved_at.strftime("%Y-%m-%d %H:%M") if r.resolved_at else "",
        ])
    return response


# ---------------------------------------------------------------------------
# Status badge colours
# ---------------------------------------------------------------------------
STATUS_COLOURS = {
    "pending":     ("🟡", "#b45309", "#fef3c7"),
    "assigned":    ("🔵", "#1d4ed8", "#dbeafe"),
    "in_progress": ("🟠", "#c2410c", "#ffedd5"),
    "resolved":    ("🟢", "#15803d", "#dcfce7"),
    "rejected":    ("🔴", "#b91c1c", "#fee2e2"),
}


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "status_badge",
        "reporter_link",
        "area_link",
        "map_link",
        "before_thumb",
        "created_at",
        "days_open",
    ]
    list_filter = ["status", "area", "created_at"]
    search_fields = ["title", "description", "reporter__username", "reporter__email"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_per_page = 25
    show_full_result_count = True
    actions = [mark_resolved, mark_rejected, reset_pending, export_csv]

    readonly_fields = [
        "reporter",
        "area",
        "created_at",
        "updated_at",
        "resolved_at",
        "before_photo_preview",
        "after_photo_preview",
        "map_embed",
        "status_badge",
    ]

    fieldsets = (
        (
            "📋  Report Info",
            {
                "fields": (
                    "status_badge",
                    "reporter",
                    "area",
                    "title",
                    "description",
                    "status",
                    "resolved_at",
                )
            },
        ),
        (
            "📍  Location",
            {
                "fields": ("latitude", "longitude", "map_embed"),
                "classes": ("collapse",),
            },
        ),
        (
            "📸  Photos",
            {
                "fields": (
                    "before_photo",
                    "before_photo_preview",
                    "after_photo",
                    "after_photo_preview",
                ),
            },
        ),
        (
            "🕒  Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # ------------------------------------------------------------------
    # Custom columns
    # ------------------------------------------------------------------
    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        icon, color, bg = STATUS_COLOURS.get(obj.status, ("⚪", "#374151", "#f3f4f6"))
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;'
            'font-size:12px;font-weight:600;">{} {}</span>',
            bg, color, icon, label,
        )

    @admin.display(description="Reporter", ordering="reporter__username")
    def reporter_link(self, obj):
        if not obj.reporter:
            return "—"
        url = f"/admin/accounts/user/{obj.reporter.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.reporter.username)

    @admin.display(description="Area", ordering="area__name")
    def area_link(self, obj):
        if not obj.area:
            return format_html('<span style="color:#9ca3af;">Unassigned</span>')
        url = f"/admin/areas/area/{obj.area.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.area.name)

    @admin.display(description="📍 Map")
    def map_link(self, obj):
        url = f"https://www.openstreetmap.org/?mlat={obj.latitude}&mlon={obj.longitude}#map=16/{obj.latitude}/{obj.longitude}"
        return format_html(
            '<a href="{}" target="_blank" style="font-size:18px;" title="View on map">🗺️</a>',
            url,
        )

    @admin.display(description="Before")
    def before_thumb(self, obj):
        if obj.before_photo:
            return format_html(
                '<img src="{}" style="height:48px;width:64px;object-fit:cover;'
                'border-radius:6px;border:1px solid #e5e7eb;" />',
                obj.before_photo.url,
            )
        return "—"

    @admin.display(description="Open (days)")
    def days_open(self, obj):
        if obj.status == Report.Status.RESOLVED and obj.resolved_at:
            delta = (obj.resolved_at - obj.created_at).days
            return format_html('<span style="color:#15803d;font-weight:600;">{} d ✓</span>', delta)
        delta = (timezone.now() - obj.created_at).days
        colour = "#b91c1c" if delta > 7 else "#b45309" if delta > 3 else "#374151"
        return format_html('<span style="color:{};">{} d</span>', colour, delta)

    @admin.display(description="Before Photo")
    def before_photo_preview(self, obj):
        if obj.before_photo:
            return format_html(
                '<img src="{}" style="max-height:220px;border-radius:8px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.15);" />',
                obj.before_photo.url,
            )
        return "No photo uploaded."

    @admin.display(description="After Photo")
    def after_photo_preview(self, obj):
        if obj.after_photo:
            return format_html(
                '<img src="{}" style="max-height:220px;border-radius:8px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.15);" />',
                obj.after_photo.url,
            )
        return "No after photo yet."

    @admin.display(description="Location Map")
    def map_embed(self, obj):
        lat, lng = float(obj.latitude), float(obj.longitude)
        return format_html(
            '<iframe width="100%" height="260" frameborder="0" style="border-radius:8px;" '
            'src="https://www.openstreetmap.org/export/embed.html?bbox={},{},{},{}'
            '&amp;layer=mapnik&amp;marker={},{}" '
            'allowfullscreen></iframe>'
            '<br><small><a href="https://www.openstreetmap.org/?mlat={}&mlon={}#map=16/{}/{}" '
            'target="_blank">Open full map ↗</a></small>',
            lng - 0.005, lat - 0.005, lng + 0.005, lat + 0.005, lat, lng,
            lat, lng, lat, lng,
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("reporter", "area")
