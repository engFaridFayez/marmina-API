from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from stages.models import Stage, Family
from results.models import (
    Subject,
    Exam,
    StudentEnrollment,
    Result,
)


User = get_user_model()


class Command(BaseCommand):

    help = "Create dummy data for development and API testing"

    PASSWORD = "Test@123456"

    def handle(self, *args, **options):

        with transaction.atomic():

            self.stdout.write(
                self.style.WARNING(
                    "Creating dummy data..."
                )
            )

            # ==================================================
            # Stage
            # ==================================================

            stage, _ = Stage.objects.get_or_create(
                name="إعدادي"
            )

            # ==================================================
            # Families
            # ==================================================

            family1, _ = Family.objects.get_or_create(
                name="أسرة الأنبا أنطونيوس",
                year="رابعة",
                defaults={
                    "stage": stage,
                }
            )

            family1.stage = stage
            family1.year = "رابعة"
            family1.save()

            family2, _ = Family.objects.get_or_create(
                name="أسرة الأنبا بيشوي",
                year="خامسة",
                defaults={
                    "stage": stage,
                }
            )

            family2.stage = stage
            family2.year = "خامسة"
            family2.save()

            family3, _ = Family.objects.get_or_create(
                name="أسرة الأنبا بولا",
                year="سادسة",
                defaults={
                    "stage": stage,
                }
            )

            family3.stage = stage
            family3.year = "سادسة"
            family3.save()

            # ==================================================
            # Family Chain
            # ==================================================

            family1.next_family = family2
            family1.save(
                update_fields=["next_family"]
            )

            family2.next_family = family3
            family2.save(
                update_fields=["next_family"]
            )

            family3.next_family = None
            family3.save(
                update_fields=["next_family"]
            )

            # ==================================================
            # Subjects
            # ==================================================

            subjects_data = [
                ("الكتاب المقدس", 100, 50),
                ("العقيدة", 100, 50),
                ("الطقس", 100, 50),
                ("الألحان", 100, 50),
                ("التاريخ الكنسي", 100, 50),
            ]

            subjects = []

            for name, final_grade, success_grade in subjects_data:

                subject, _ = Subject.objects.get_or_create(
                    name=name,
                    defaults={
                        "final_grade": final_grade,
                        "success_grade": success_grade,
                    }
                )

                subjects.append(subject)

            # ==================================================
            # Exams
            # ==================================================

            exams_data = [
                ("الترم الأول", "2025/2026"),
                ("الترم الثاني", "2025/2026"),
                ("الترم الثالث", "2025/2026"),
            ]

            exams = []

            for name, year in exams_data:

                exam, _ = Exam.objects.get_or_create(
                    name=name,
                    year=year
                )

                exams.append(exam)

            # ==================================================
            # Leaders
            # ==================================================

            stage_leader = self.create_user(
                username="stage_leader",
                full_name="أمين مرحلة إعدادي",
                role="امين مرحلة",
            )

            head_leader = self.create_user(
                username="head_leader",
                full_name="أمين الشمامسة",
                role="امين الشمامسة",
            )

            stage.leaders.add(stage_leader)

            # ==================================================
            # Family Leaders
            # ==================================================

            family_users = []

            for index, family in enumerate(
                [family1, family2, family3],
                start=1
            ):

                leader = self.create_user(
                    username=f"family{index}_leader",
                    full_name=f"أمين {family.name}",
                    role="امين اسرة",
                    family=family,
                )

                assistant = self.create_user(
                    username=f"family{index}_assistant",
                    full_name=f"مساعد {family.name}",
                    role="امين مساعد اسرة",
                    family=family,
                )

                servant = self.create_user(
                    username=f"family{index}_servant",
                    full_name=f"خادم {family.name}",
                    role="خادم",
                    family=family,
                )

                family_users.extend([
                    leader,
                    assistant,
                    servant,
                ])

            # ==================================================
            # Students
            # ==================================================

            families = [
                family1,
                family2,
                family3,
            ]

            first_names = [
                "فريد",
                "مينا",
                "جرجس",
                "مارك",
                "كيرلس",
                "بطرس",
                "يوسف",
                "ميناوي",
                "أنطون",
                "كيرو",
            ]

            student_counter = 1

            for family_index, family in enumerate(
                families,
                start=1
            ):

                for i in range(10):

                    username = (
                        f"student{student_counter}"
                    )

                    student = self.create_user(
                        username=username,
                        full_name=(
                            f"{first_names[i]} "
                            f"{family.year}"
                        ),
                        role="مخدوم",
                        family=family,
                    )

                    # ==========================================
                    # Enrollment
                    # ==========================================

                    enrollment, _ = (
                        StudentEnrollment.objects.get_or_create(
                            student=student,
                            family=family,
                            academic_year="2025/2026",
                            defaults={
                                "status": None
                            }
                        )
                    )

                    # ==========================================
                    # Results
                    # ==========================================

                    for exam_index, exam in enumerate(
                        exams
                    ):

                        for subject_index, subject in enumerate(
                            subjects
                        ):

                            # Make some students pass
                            # and some fail intentionally.

                            if i % 5 == 0:

                                points = (
                                    subject.success_grade + 20
                                )

                            elif i % 5 == 1:

                                points = (
                                    subject.success_grade - 10
                                )

                            else:

                                points = (
                                    subject.success_grade + 10
                                )

                            # Keep points inside valid range

                            points = min(
                                points,
                                subject.final_grade
                            )

                            points = max(
                                points,
                                0
                            )

                            Result.objects.get_or_create(
                                enrollment=enrollment,
                                subject=subject,
                                exam=exam,
                                defaults={
                                    "points": points
                                }
                            )

                    student_counter += 1

            # ==================================================
            # Admin
            # ==================================================

            admin = self.create_user(
                username="admin",
                full_name="System Admin",
                role="admin",
                is_staff=True,
                is_superuser=True,
            )

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Dummy data created successfully!"
                )
            )

            self.stdout.write("")
            self.stdout.write(
                "Password for all dummy users:"
            )

            self.stdout.write(
                self.style.WARNING(
                    self.PASSWORD
                )
            )

            self.stdout.write("")

            self.stdout.write(
                "Admin:"
            )
            self.stdout.write(
                "  username: admin"
            )

            self.stdout.write("")

            self.stdout.write(
                "Stage Leader:"
            )
            self.stdout.write(
                "  username: stage_leader"
            )

            self.stdout.write("")

            self.stdout.write(
                "Head:"
            )
            self.stdout.write(
                "  username: head_leader"
            )

            self.stdout.write("")

            self.stdout.write(
                "Family 1:"
            )
            self.stdout.write(
                "  family1_leader"
            )
            self.stdout.write(
                "  family1_assistant"
            )
            self.stdout.write(
                "  family1_servant"
            )

            self.stdout.write("")

            self.stdout.write(
                "Family 2:"
            )
            self.stdout.write(
                "  family2_leader"
            )
            self.stdout.write(
                "  family2_assistant"
            )
            self.stdout.write(
                "  family2_servant"
            )

            self.stdout.write("")

            self.stdout.write(
                "Family 3:"
            )
            self.stdout.write(
                "  family3_leader"
            )
            self.stdout.write(
                "  family3_assistant"
            )
            self.stdout.write(
                "  family3_servant"
            )

    # ======================================================
    # Create User
    # ======================================================

    def create_user(
        self,
        username,
        full_name,
        role,
        family=None,
        is_staff=False,
        is_superuser=False,
    ):

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "full_name": full_name,
                "role": role,
                "family": family,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            }
        )

        user.full_name = full_name
        user.role = role
        user.family = family
        user.is_staff = is_staff
        user.is_superuser = is_superuser

        user.set_password(
            self.PASSWORD
        )

        user.save()

        return user