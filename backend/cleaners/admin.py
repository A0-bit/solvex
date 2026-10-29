from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Cleaner


@admin.action(description="✅  Activate selected cleaners")
def activate_cleaners(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="🚫  Deactivate selected cleaners")
def deactivate_cleaners(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Cleaner)
class CleanerAdmin(admin.ModelAdmin):
    list_display  = [
        "full_name",
        "username_link",
        "area_link",
        "assignment_count",
        "active_badge",
        "created_at",
    ]
    list_filter   = ["is_active", "area"]
    search_fields = ["user__username", "user__email", "user__first_name", "user__last_name"]
    list_per_page = 25
    actions = [activate_cleaners, deactivate_cleaners]
    readonly_fields = ["assignment_count", "created_at"]

    fieldsets = (
        (
            "👷  Cleaner Info",
            {"fields": ("user", "area", "is_active")},
        ),
        (
            "📊  Activity",
            {"fields": ("assignment_count", "created_at"), "classes": ("collapse",)},
        ),
    )

    # ------------------------------------------------------------------
    # Custom columns
    # ------------------------------------------------------------------
    @admin.display(description="Name", ordering="user__first_name")
    def full_name(self, obj):
        name = obj.user.get_full_name()
        return name if name.strip() else "—"

    @admin.display(description="Username", ordering="user__username")
    def username_link(self, obj):
        url = f"/admin/accounts/user/{obj.user.pk}/change/"
        return format_html('<a href="{}">@{}</a>', url, obj.user.username)

    @admin.display(description="Area", ordering="area__name")
    def area_link(self, obj):
        if not obj.area:
            return format_html('<span style="color:#9ca3af;">—</span>')
        url = f"/admin/areas/area/{obj.area.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.area.name)

    @admin.display(description="Assignments", ordering="assignment_count")
    def assignment_count(self, obj):
        count = getattr(obj, "assignment_count", obj.assignments.count())
        if count == 0:
            return format_html('<span style="color:#9ca3af;">0</span>')
        url = f"/admin/assignments/assignment/?cleaner__id__exact={obj.pk}"
        return format_html('<a href="{}" style="font-weight:600;">{}</a>', url, count)

    @admin.display(description="Status", ordering="is_active", boolean=False)
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#dcfce7;color:#15803d;padding:2px 10px;'
                'border-radius:12px;font-size:11px;font-weight:700;">● Active</span>'
            )
        return format_html(
            '<span style="background:#f3f4f6;color:#9ca3af;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">● Inactive</span>'
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            assignment_count=Count("assignments")
        ).select_related("user", "area")
