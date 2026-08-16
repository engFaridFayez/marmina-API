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

    subject = serializers.SerializerMethodField()

    component = serializers.SerializerMethodField()

    exam = serializers.SerializerMethodField()

    max_grade = serializers.SerializerMethodField()

    final_grade = serializers.SerializerMethodField()

    success_grade = serializers.SerializerMethodField()

    is_success = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "student",
            "subject",
            "component",
            "exam",
            "points",
            "max_grade",
            "final_grade",
            "success_grade",
            "is_success",
        ]

    def get_subject(self, obj):
        if obj.subject_exam:
            return obj.subject_exam.subject.name

        if obj.component_exam:
            return obj.component_exam.component.subject.name

        return None

    def get_component(self, obj):
        if obj.component_exam:
            return obj.component_exam.component.name

        return None

    def get_exam(self, obj):
        if obj.subject_exam:
            return obj.subject_exam.exam.name

        if obj.component_exam:
            return obj.component_exam.exam.name

        return None

    def get_max_grade(self, obj):
        if obj.subject_exam:
            return obj.subject_exam.max_grade

        if obj.component_exam:
            return obj.component_exam.max_grade

        return None

    def get_final_grade(self, obj):
        if obj.subject_exam:
            return obj.subject_exam.subject.final_grade

        if obj.component_exam:
            return obj.component_exam.component.subject.final_grade

        return None

    def get_success_grade(self, obj):
        if obj.subject_exam:
            return obj.subject_exam.success_grade

        if obj.component_exam:
            return obj.component_exam.success_grade

        return None
    def get_is_success(self, obj):
        return obj.is_success()


class ResultWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = [
            "subject_exam",
            "component_exam",
            "points",
        ]

    def validate(self, attrs):

        subject_exam = attrs.get("subject_exam")

        component_exam = attrs.get("component_exam")

        points = attrs.get("points")

        # =========================
        # Subject / Component
        # =========================

        if self.instance:

            if subject_exam is None:
                subject_exam = self.instance.subject_exam

            if component_exam is None:
                component_exam = self.instance.component_exam

            if points is None:
                points = self.instance.points

        # لازم واحد فقط
        if bool(subject_exam) == bool(component_exam):
            raise serializers.ValidationError({
                "detail": (
                    "يجب تحديد المادة أو الجزء "
                    "وليس الاثنين معًا."
                )
            })

        # =========================
        # Points
        # =========================

        if points < 0:
            raise serializers.ValidationError({
                "points": "الدرجة لا يمكن أن تكون أقل من صفر."
            })

        # =========================
        # Max Grade
        # =========================

        if subject_exam:
            max_grade = subject_exam.max_grade

        else:
            max_grade = component_exam.max_grade

        if points > max_grade:
            raise serializers.ValidationError({
                "points": (
                    f"الدرجة لا يمكن أن تتجاوز "
                    f"{max_grade}."
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


from results.models import SubjectExam, SubjectComponent, ComponentExam


class SubjectExamSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(
        source="subject.name", read_only=True
    )
    exam_name = serializers.CharField(
        source="exam.name", read_only=True
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
        subject = attrs.get("subject") or getattr(self.instance, "subject", None)
        max_grade = attrs.get("max_grade") or getattr(self.instance, "max_grade", None)
        success_grade = attrs.get("success_grade", None)

        if success_grade is not None and max_grade is not None and success_grade > max_grade:
            raise serializers.ValidationError({
                "success_grade": "درجة النجاح لا يمكن أن تتجاوز الدرجة القصوى."
            })

        return attrs


class SubjectComponentSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(
        source="subject.name", read_only=True
    )

    class Meta:
        model = SubjectComponent
        fields = [
            "id",
            "subject",
            "subject_name",
            "name",
        ]


class ComponentExamSerializer(serializers.ModelSerializer):

    component_name = serializers.CharField(
        source="component.name", read_only=True
    )
    subject_name = serializers.CharField(
        source="component.subject.name", read_only=True
    )
    exam_name = serializers.CharField(
        source="exam.name", read_only=True
    )

    class Meta:
        model = ComponentExam
        fields = [
            "id",
            "component",
            "component_name",
            "subject_name",
            "exam",
            "exam_name",
            "max_grade",
            "success_grade",
        ]