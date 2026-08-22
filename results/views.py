from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from users.models import CustomUser
from stages.models import Family
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from results.permissions import can_manage_family, can_manage_student, can_manage_enrollment
from results.models import (
    Exam,
    Result,
    Subject,
    StudentEnrollment,
    SubjectExam,
)

from results.serializers import (
    ExamSerializer,
    ResultSerializer,
    SubjectSerializer,
    StudentEnrollmentSerializer,
    ResultWriteSerializer,
    SubjectExamSerializer,
)



# =========================
# Student Results
# =========================

class MyResults(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        student = request.user
        exam_id = request.GET.get("exam")
        enrollment_id = request.GET.get("enrollment")

        results = Result.objects.filter(
            enrollment__student=student
        )

        if exam_id:
            results = results.filter(
                Q(subject_exam__exam_id=exam_id) |
                Q(component_exam__exam_id=exam_id)
            )

        if enrollment_id:
            results = results.filter(
                enrollment_id=enrollment_id
            )

        serializer = ResultSerializer(
            results,
            many=True
        )

        return Response(serializer.data)


# =========================
# Subjects
# =========================

class Subjects(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        subjects = Subject.objects.all()

        serializer = SubjectSerializer(
            subjects,
            many=True
        )

        return Response(serializer.data)


# =========================
# Exams
# =========================

class Exams(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        exams = Exam.objects.all()

        serializer = ExamSerializer(
            exams,
            many=True
        )

        return Response(serializer.data)



class FamilyStudents(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, family_id):

        family = get_object_or_404(
            Family.objects.select_related(
                "stage",
                "next_family",
                "next_family__stage",
            ),
            id=family_id
        )

        if not can_manage_family(request.user, family):
            return Response(
                {
                    "detail": "ليس لديك صلاحية الوصول إلى هذه الأسرة."
                },
                status=403
            )

        students = CustomUser.objects.filter(
            family=family,
            role="مخدوم"
        ).order_by("full_name")

        data = []

        for student in students:
            data.append({
                "id": student.id,
                "full_name": student.full_name,
                "image": (
                    request.build_absolute_uri(student.image.url)
                    if student.image
                    else None
                ),
            })

        return Response({
            "family": {
                "id": family.id,
                "name": family.name,
                "year": family.year,
                "stage": (
                    family.stage.name
                    if family.stage
                    else None
                ),
            },

            "next_family": (
                {
                    "id": family.next_family.id,
                    "name": family.next_family.name,
                    "year": family.next_family.year,
                    "stage": (
                        family.next_family.stage.name
                        if family.next_family.stage
                        else None
                    ),
                }
                if family.next_family
                else None
            ),

            "students": data,
        })
class StudentEnrollments(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):

        student = get_object_or_404(
            CustomUser,
            id=student_id,
            role="مخدوم"
        )

        if not can_manage_student(
            request.user,
            student
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية الوصول إلى هذا الطالب."
                },
                status=403
            )

        enrollments = StudentEnrollment.objects.filter(
            student=student
        ).select_related(
            "student",
            "family",
            "family__stage",
        ).order_by(
            "-academic_year"
        )

        serializer = StudentEnrollmentSerializer(
            enrollments,
            many=True
        )

        return Response(serializer.data)

class EnrollmentResults(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, enrollment_id):

        enrollment = get_object_or_404(
            StudentEnrollment.objects.select_related(
                "student",
                "family",
                "family__stage",
            ),
            id=enrollment_id
        )

        if not can_manage_enrollment(
            request.user,
            enrollment
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية الوصول إلى نتائج هذا المخدوم."
                },
                status=403
            )

        results = Result.objects.filter(
            enrollment=enrollment
        ).select_related(
            "enrollment__student",
            "subject_exam__subject",
            "subject_exam__exam",
            "component_exam__component__subject",
            "component_exam__exam",
        )

        serializer = ResultSerializer(
            results,
            many=True
        )

        return Response(serializer.data)

    def post(self, request, enrollment_id):

        enrollment = get_object_or_404(
            StudentEnrollment.objects.select_related(
                "student",
                "family",
                "family__stage",
            ),
            id=enrollment_id
        )

        if not can_manage_enrollment(
            request.user,
            enrollment
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية إضافة نتيجة لهذا المخدوم."
                },
                status=403
            )

        serializer = ResultWriteSerializer(
            data=request.data,
            context={
                "enrollment": enrollment
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            with transaction.atomic():

                result = serializer.save(
                    enrollment=enrollment
                )

        except IntegrityError:

            return Response(
                {
                    "detail": (
                        "توجد نتيجة بالفعل لهذه المادة "
                        "في هذا الامتحان."
                    )
                },
                status=400
            )

        return Response(
            ResultSerializer(result).data,
            status=201
        )

class ResultDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, result_id):

        result = get_object_or_404(
            Result.objects.select_related(
                "enrollment__family",
                "enrollment__family__stage",
            ),
            id=result_id
        )

        if not can_manage_enrollment(
            request.user,
            result.enrollment
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية تعديل هذه النتيجة."
                },
                status=403
            )

        serializer = ResultWriteSerializer(
            result,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = serializer.save()

        return Response(
            ResultSerializer(result).data
        )

    def delete(self, request, result_id):

        result = get_object_or_404(
            Result.objects.select_related(
                "enrollment__family",
                "enrollment__family__stage",
            ),
            id=result_id
        )

        if not can_manage_enrollment(
            request.user,
            result.enrollment
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية حذف هذه النتيجة."
                },
                status=403
            )

        result.delete()

        return Response(
            status=204
        )

class PromoteStudents(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, family_id):

        family = get_object_or_404(
            Family.objects.select_related(
                "stage",
                "next_family",
            ),
            id=family_id
        )

        # =========================
        # Check permission
        # =========================

        if not can_manage_family(
            request.user,
            family
        ):
            return Response(
                {
                    "detail": "ليس لديك صلاحية نقل المخدومين من هذه الأسرة."
                },
                status=403
            )

        # =========================
        # Next family
        # =========================

        if not family.next_family:
            return Response(
                {
                    "detail": "لا توجد أسرة تالية."
                },
                status=400
            )

        next_family = family.next_family

        # =========================
        # Students
        # =========================

        passed_ids = request.data.get(
            "passed_student_ids",
            []
        )

        failed_ids = request.data.get(
            "failed_student_ids",
            []
        )

        # =========================
        # Validate selection
        # =========================

        if not passed_ids and not failed_ids:
            return Response(
                {
                    "detail": "حدد الناجحين والراسبين."
                },
                status=400
            )

        # =========================
        # Prevent duplicate selection
        # =========================

        all_ids = set(
            passed_ids + failed_ids
        )

        if len(all_ids) != (
            len(passed_ids) +
            len(failed_ids)
        ):
            return Response(
                {
                    "detail": "لا يمكن أن يكون المخدوم ناجح وراسب في نفس الوقت."
                },
                status=400
            )

        # =========================
        # Get students
        # =========================

        students = CustomUser.objects.filter(
            id__in=all_ids,
            family=family,
            role="مخدوم"
        )

        if students.count() != len(all_ids):
            return Response(
                {
                    "detail": "بعض المخدومين غير موجودين في هذه الأسرة."
                },
                status=400
            )

        # =========================
        # Current academic year
        # =========================

        current_enrollments = {
            enrollment.student_id: enrollment
            for enrollment in StudentEnrollment.objects.filter(
                student_id__in=all_ids,
                family=family
            ).order_by(
                "-academic_year"
            )
        }

        # =========================
        # Promote
        # =========================

        with transaction.atomic():

            for student in students:

                current_enrollment = current_enrollments.get(
                    student.id
                )

                if not current_enrollment:
                    return Response(
                        {
                            "detail": (
                                f"لا يوجد سجل دراسي "
                                f"لـ {student.full_name} "
                                f"في هذه الأسرة."
                            )
                        },
                        status=400
                    )

                # =====================
                # Passed
                # =====================

                if student.id in passed_ids:

                    current_enrollment.status = "ناجح"

                    current_enrollment.save(
                        update_fields=["status"]
                    )

                    new_enrollment, created = (
                        StudentEnrollment.objects.get_or_create(
                            student=student,
                            family=next_family,
                            academic_year=next_family.year,
                            defaults={
                                "status": None
                            }
                        )
                    )

                    student.family = next_family

                    student.save(
                        update_fields=["family"]
                    )

                # =====================
                # Failed
                # =====================

                else:

                    current_enrollment.status = "راسب"

                    current_enrollment.save(
                        update_fields=["status"]
                    )

                    StudentEnrollment.objects.get_or_create(
                        student=student,
                        family=family,
                        academic_year=next_family.year,
                        defaults={
                            "status": None
                        }
                    )

        return Response(
            {
                "detail": "تم نقل المخدومين بنجاح.",
                "passed_count": len(passed_ids),
                "failed_count": len(failed_ids),
            }
        )



class ResultFamilies(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        user = request.user

        # =========================
        # Admin / أمين الشمامسة
        # =========================

        if user.role == "admin" or user.is_superuser:
            families = Family.objects.all()

        elif user.role == "امين الشمامسة":
            families = Family.objects.all()

        # =========================
        # أمين المرحلة
        # =========================

        elif user.role == "امين مرحلة":
            families = Family.objects.filter(
                stage__leaders=user
            )

        # =========================
        # أمين الأسرة / المساعد / الخادم
        # =========================

        elif user.role in [
            "خادم عادي",
            "امين اسرة",
            "امين مساعد اسرة",
        ]:
            families = Family.objects.filter(
                id=user.family_id
            )

        # =========================
        # أي مستخدم آخر
        # =========================

        else:
            families = Family.objects.none()

        families = families.select_related(
            "stage",
            "next_family",
        ).order_by(
            "stage__name",
            "name"
        )

        data = []

        for family in families:

            students_count = CustomUser.objects.filter(
                family=family,
                role="مخدوم"
            ).count()

            data.append({
                "id": family.id,
                "name": family.name,
                "year": family.year,
                "stage": (
                    family.stage.name
                    if family.stage
                    else None
                ),
                "students_count": students_count,
            })

        return Response(data)



class Subjects(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = serializer.save()
        return Response(SubjectSerializer(subject).data, status=201)


class SubjectDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        subject = serializer.save()
        return Response(SubjectSerializer(subject).data)

    def delete(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()
        return Response(status=204)


# =========================
# Exams
# =========================

class Exams(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()
        return Response(ExamSerializer(exam).data, status=201)


class ExamDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()
        return Response(ExamSerializer(exam).data)

    def delete(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return Response(status=204)


# =========================
# Subject Exams (join records)
# =========================

class SubjectExams(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subject_exams = SubjectExam.objects.select_related("subject", "exam")

        exam_id = request.GET.get("exam")
        subject_id = request.GET.get("subject")

        if exam_id:
            subject_exams = subject_exams.filter(exam_id=exam_id)

        if subject_id:
            subject_exams = subject_exams.filter(subject_id=subject_id)

        serializer = SubjectExamSerializer(subject_exams, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subject_exam = serializer.save()
        except IntegrityError:
            return Response(
                {"detail": "توجد بالفعل درجة لهذه المادة في هذا الامتحان."},
                status=400
            )

        return Response(SubjectExamSerializer(subject_exam).data, status=201)


class SubjectExamDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, subject_exam_id):
        subject_exam = get_object_or_404(SubjectExam, id=subject_exam_id)
        serializer = SubjectExamSerializer(subject_exam, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        subject_exam = serializer.save()
        return Response(SubjectExamSerializer(subject_exam).data)

    def delete(self, request, subject_exam_id):
        subject_exam = get_object_or_404(SubjectExam, id=subject_exam_id)
        subject_exam.delete()
        return Response(status=204)
