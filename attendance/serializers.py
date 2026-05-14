from rest_framework import serializers

from attendance.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source="student.full_name")
    term = serializers.CharField(source="term.name")
    class Meta:
        model = Attendance
        fields = [
            'id',
            "student",
            "term",
            "date",
            "is_present_mass",
            "is_present_family",
            "created_at",
        ]