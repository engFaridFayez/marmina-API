from rest_framework import serializers

from results.models import Exam, Result, Subject

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = [
            'name',
            'final_grade',
            'success_grade',
        ]

class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'year',
        ]

class ResultSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source="student.full_name")
    subject = serializers.CharField(source="subject.name")
    exam = serializers.CharField(source="exam.name")
    final_grade = serializers.IntegerField(source="subject.final_grade")
    success_grade = serializers.IntegerField(source="subject.success_grade")
    is_success = serializers.SerializerMethodField()


    class Meta:
        model = Result
        fields = [
            'student',
            'subject',
            'exam',
            'points',
            'final_grade',
            "success_grade",
            'is_success'
        ]

    def get_is_success(self, obj):
        return obj.is_success()