from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html

from .models import User


ROLE_COLOURS = {
    "superadmin": ("#7c3aed", "#ede9fe"),
    "supervisor":  ("#1d4ed8", "#dbeafe"),
    "user":        ("#15803d", "#dcfce7"),
}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "avatar_thumb",
        "username",
        "email",
        "role_badge",
        "phone",
        "report_count",
        "is_active",
        "date_joined",
    ]
    list_filter   = ["role", "is_active", "is_staff"]
    search_fields = ["username", "email", "phone", "first_name", "last_name"]
    ordering      = ["-date_joined"]
    list_per_page = 25
    readonly_fields = ["avatar_preview", "date_joined", "last_login", "report_count"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "👤  Profile",
            {"fields": ("role", "phone", "avatar", "avatar_preview")},
        ),
        (
            "📊  Activity",
            {"fields": ("report_count",), "classes": ("collapse",)},
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "👤  Profile",
            {"fields": ("role", "phone", "email")},
        ),
    )

    # ------------------------------------------------------------------
    # Custom columns
    # ------------------------------------------------------------------
    @admin.display(description="")
    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:32px;width:32px;border-radius:50%;'
                'object-fit:cover;border:2px solid #e5e7eb;" />',
                obj.avatar.url,
            )
        initials = (obj.first_name[:1] + obj.last_name[:1]) or obj.username[:2]
        return format_html(
            '<div style="height:32px;width:32px;border-radius:50%;background:#d1fae5;'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:12px;font-weight:700;color:#065f46;">{}</div>',
            initials.upper(),
        )

    @admin.display(description="Role", ordering="role")
    def role_badge(self, obj):
        color, bg = ROLE_COLOURS.get(obj.role, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:12px;'
            'font-size:11px;font-weight:700;text-transform:uppercase;">{}</span>',
            bg, color, obj.role,
        )

    @admin.display(description="Reports", ordering="report_count")
    def report_count(self, obj):
        count = getattr(obj, "report_count", None)
        if count is None:
            count = obj.reports.count()
        if count == 0:
            return format_html('<span style="color:#9ca3af;">0</span>')
        url = f"/admin/reports/report/?reporter__id__exact={obj.pk}"
        return format_html('<a href="{}" style="font-weight:600;">{}</a>', url, count)

    @admin.display(description="Avatar")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:12px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.15);" />',
                obj.avatar.url,
            )
        return "No avatar uploaded."

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(report_count=Count("reports"))
