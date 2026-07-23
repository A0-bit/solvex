from django.contrib import admin
from cleaners.models import Cleaner
from .models import Area


class CleanerInline(admin.TabularInline):
    model = Cleaner
    extra = 0
    fields = ["user", "is_active"]
    readonly_fields = ["user"]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ["name", "supervisor", "created_at"]
    search_fields = ["name", "supervisor__username"]
    inlines = [CleanerInline]
