from rest_framework import serializers

from results.models import (
    Exam,
    Result,
    Subject,
    StudentEnrollment,
)


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "final_grade",
            "success_grade",
        ]


class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "year",
        ]


class ResultSerializer(serializers.ModelSerializer):

    student = serializers.CharField(
        source="enrollment.student.full_name",
        read_only=True
    )

    subject = serializers.CharField(
        source="subject.name",
        read_only=True
    )

    exam = serializers.CharField(
        source="exam.name",
        read_only=True
    )

    final_grade = serializers.IntegerField(
        source="subject.final_grade",
        read_only=True
    )

    success_grade = serializers.IntegerField(
        source="subject.success_grade",
        read_only=True
    )

    is_success = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "student",
            "subject",
            "exam",
            "points",
            "final_grade",
            "success_grade",
            "is_success",
        ]

    def get_is_success(self, obj):
        return obj.is_success()


class ResultWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = [
            "subject",
            "exam",
            "points",
        ]

    def validate(self, attrs):

        # =========================
        # Subject
        # =========================

        subject = attrs.get("subject")

        if subject is None and self.instance:
            subject = self.instance.subject

        # =========================
        # Points
        # =========================

        points = attrs.get("points")

        if points is None and self.instance:
            points = self.instance.points

        if points < 0:
            raise serializers.ValidationError({
                "points": "الدرجة لا يمكن أن تكون أقل من صفر."
            })

        if points > subject.final_grade:
            raise serializers.ValidationError({
                "points": (
                    f"الدرجة لا يمكن أن تتجاوز "
                    f"{subject.final_grade}."
                )
            })

        # =========================
        # Duplicate Result
        # =========================

        if self.instance:

            enrollment = self.instance.enrollment
            exam = attrs.get("exam", self.instance.exam)

        else:

            enrollment = self.context.get("enrollment")
            exam = attrs.get("exam")

        if enrollment and subject and exam:

            exists = Result.objects.filter(
                enrollment=enrollment,
                subject=subject,
                exam=exam,
            )

            # في حالة التعديل:
            # نستبعد النتيجة الحالية من البحث
            if self.instance:
                exists = exists.exclude(
                    id=self.instance.id
                )

            if exists.exists():
                raise serializers.ValidationError({
                    "detail": (
                        "توجد نتيجة بالفعل لهذه المادة "
                        "في هذا الامتحان."
                    )
                })

        return attrs

class StudentEnrollmentSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.full_name",
        read_only=True
    )

    family_name = serializers.CharField(
        source="family.name",
        read_only=True
    )

    stage_name = serializers.CharField(
        source="family.stage.name",
        read_only=True
    )
    status = serializers.CharField(
        read_only=True
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "student",
            "student_name",
            "family",
            "family_name",
            "stage_name",
            "academic_year",
            "status",
        ]