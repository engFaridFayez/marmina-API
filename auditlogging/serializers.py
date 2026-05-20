from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.username", read_only=True)
    target_name = serializers.CharField(source="target_user.username", read_only=True)

    class Meta:
        model = ActivityLog
        fields = "__all__"