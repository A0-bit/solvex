from rest_framework import serializers
from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Area
        fields = ["id", "name", "boundary", "supervisor", "supervisor_name", "created_at"]
        read_only_fields = ["created_at"]

    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return obj.supervisor.get_full_name() or obj.supervisor.username
        return None
