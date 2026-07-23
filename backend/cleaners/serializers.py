from rest_framework import serializers
from accounts.serializers import UserProfileSerializer
from .models import Cleaner


class CleanerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=__import__("accounts.models", fromlist=["User"]).User.objects.filter(role="user"),
        write_only=True,
    )
    area_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cleaner
        fields = ["id", "user", "user_id", "area", "area_name", "is_active", "created_at"]
        read_only_fields = ["created_at"]

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None
