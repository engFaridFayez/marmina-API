from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from results.models import Exam, Result, Subject
from results.serializers import ExamSerializer, ResultSerializer, SubjectSerializer
# Create your views here.

class MyResults(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        student = request.user
        exam_id = request.GET.get("exam")
        results = Result.objects.filter(student=student)
        if exam_id:
            results = results.filter(exam = exam_id)
        serializer = ResultSerializer(results,many=True)

        return Response(serializer.data)
    
class Subjects(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):

        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects,many=True)
        return Response(serializer.data)
    
class Exams(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        exams = Exam.objects.all()
        serialzier = ExamSerializer(exams,many=True)
        return Response(serialzier.data)