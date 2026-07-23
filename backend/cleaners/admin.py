from django.contrib import admin
from .models import Cleaner


@admin.register(Cleaner)
class CleanerAdmin(admin.ModelAdmin):
    list_display = ["user", "area", "is_active", "created_at"]
    list_filter = ["is_active", "area"]
    search_fields = ["user__username", "user__email"]
