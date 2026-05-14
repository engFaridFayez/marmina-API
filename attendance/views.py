from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import permissions

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer

# Create your views here.
class StudentAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        student = request.user
        term_id = request.GET.get("term")

        attendance = Attendance.objects.filter(student=student).order_by("-date")

        if term_id:
            attendance = attendance.filter(term = term_id)
        serializer = AttendanceSerializer(attendance,many=True)

        return Response(serializer.data)