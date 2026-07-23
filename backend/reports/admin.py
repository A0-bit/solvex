from django.contrib import admin
from django.utils.html import format_html
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "reporter", "area", "created_at"]
    list_filter = ["status", "area"]
    search_fields = ["title", "description", "reporter__username"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "reporter",
        "area",
        "created_at",
        "updated_at",
        "resolved_at",
        "before_photo_preview",
        "after_photo_preview",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Report Info",
            {
                "fields": (
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
            "Location",
            {"fields": ("latitude", "longitude")},
        ),
        (
            "Photos",
            {"fields": ("before_photo", "before_photo_preview", "after_photo", "after_photo_preview")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def before_photo_preview(self, obj):
        if obj.before_photo:
            return format_html('<img src="{}" style="max-height:150px;" />', obj.before_photo.url)
        return "-"
    before_photo_preview.short_description = "Before Photo Preview"

    def after_photo_preview(self, obj):
        if obj.after_photo:
            return format_html('<img src="{}" style="max-height:150px;" />', obj.after_photo.url)
        return "-"
    after_photo_preview.short_description = "After Photo Preview"
