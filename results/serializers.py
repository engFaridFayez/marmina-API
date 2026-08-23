from rest_framework import serializers

from results.models import (
    Exam,
    Result,
    Subject,
    StudentEnrollment,
    SubjectExam,
)


# =========================================================
# Subject
# =========================================================

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "final_grade",
            "success_grade",
        ]


# =========================================================
# Exam
# =========================================================

class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "year",
        ]


# =========================================================
# Result
# =========================================================

class ResultSerializer(serializers.ModelSerializer):

    student = serializers.CharField(
        source="enrollment.student.full_name",
        read_only=True
    )

    subject = serializers.CharField(
        source="subject_exam.subject.name",
        read_only=True
    )

    exam = serializers.CharField(
        source="subject_exam.exam.name",
        read_only=True
    )

    max_grade = serializers.IntegerField(
        source="subject_exam.max_grade",
        read_only=True
    )

    final_grade = serializers.IntegerField(
        source="subject_exam.subject.final_grade",
        read_only=True
    )

    success_grade = serializers.IntegerField(
        source="subject_exam.success_grade",
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
            "max_grade",
            "final_grade",
            "success_grade",
            "is_success",
        ]

    def get_is_success(self, obj):

        if not obj.subject_exam:
            return None

        return obj.points >= obj.subject_exam.success_grade


# =========================================================
# Result Write
# =========================================================

class ResultWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result

        fields = [
            "subject_exam",
            "points",
        ]

    def validate(self, attrs):

        subject_exam = attrs.get(
            "subject_exam"
        )

        points = attrs.get(
            "points"
        )

        # ==========================================
        # PATCH
        # ==========================================

        if self.instance:

            if subject_exam is None:
                subject_exam = self.instance.subject_exam

            if points is None:
                points = self.instance.points

        # ==========================================
        # SubjectExam required
        # ==========================================

        if not subject_exam:

            raise serializers.ValidationError({
                "subject_exam": "يجب تحديد المادة والامتحان."
            })

        # ==========================================
        # Points
        # ==========================================

        if points is None:

            raise serializers.ValidationError({
                "points": "يجب إدخال الدرجة."
            })

        if points < 0:

            raise serializers.ValidationError({
                "points": "الدرجة لا يمكن أن تكون أقل من صفر."
            })

        # ==========================================
        # Max Grade
        # ==========================================

        max_grade = subject_exam.max_grade

        if points > max_grade:

            raise serializers.ValidationError({
                "points": (
                    f"الدرجة لا يمكن أن تتجاوز "
                    f"{max_grade}."
                )
            })

        return attrs


# =========================================================
# Student Enrollment
# =========================================================

class StudentEnrollmentSerializer(
    serializers.ModelSerializer
):

    student_name = serializers.CharField(
        source="student.full_name",
        read_only=True
    )
    student_username = serializers.CharField(
        source="student.username",
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
            "student_username",
            "family",
            "family_name",
            "stage_name",
            "academic_year",
            "status",
        ]


# =========================================================
# SubjectExam
# =========================================================

class SubjectExamSerializer(
    serializers.ModelSerializer
):

    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True
    )

    exam_name = serializers.CharField(
        source="exam.name",
        read_only=True
    )

    class Meta:
        model = SubjectExam

        fields = [
            "id",
            "subject",
            "subject_name",
            "exam",
            "exam_name",
            "max_grade",
            "success_grade",
        ]

    def validate(self, attrs):

        subject = attrs.get(
            "subject"
        ) or getattr(
            self.instance,
            "subject",
            None
        )

        max_grade = attrs.get(
            "max_grade"
        )

        if max_grade is None and self.instance:
            max_grade = self.instance.max_grade

        success_grade = attrs.get(
            "success_grade"
        )

        if (
            success_grade is not None
            and max_grade is not None
            and success_grade > max_grade
        ):

            raise serializers.ValidationError({
                "success_grade": (
                    "درجة النجاح لا يمكن أن تتجاوز "
                    "الدرجة القصوى."
                )
            })

        return attrs