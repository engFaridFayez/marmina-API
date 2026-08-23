import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.functions import Trim

from users.models import CustomUser
from stages.models import Family

from results.models import (
    Subject,
    Exam,
    SubjectExam,
    StudentEnrollment,
    Result,
)


class Command(BaseCommand):

    help = "Import results from Excel file"

    def add_arguments(self, parser):

        parser.add_argument(
            "file",
            type=str,
            help="Path to Excel file"
        )

        parser.add_argument(
            "--academic-year",
            required=True,
            help="Academic year, example: 2025/2026"
        )

    @transaction.atomic
    def handle(self, *args, **options):

        file_path = options["file"]
        academic_year = options["academic_year"]

        # ==========================================
        # Helpers
        # ==========================================

        def clean(value):

            if pd.isna(value):
                return None

            if isinstance(value, str):
                value = value.strip()
                return value if value else None

            return value

        def normalize(value):

            value = clean(value)

            if value is None:
                return None

            value = str(value).strip()

            # توحيد الهمزات
            value = (
                value
                .replace("أ", "ا")
                .replace("إ", "ا")
                .replace("آ", "ا")
            )

            # توحيد التاء المربوطة
            value = value.replace("ة", "ه")

            # إزالة المسافات الزائدة
            value = " ".join(value.split())

            return value

        # ==========================================
        # Load Excel
        # ==========================================

        try:

            df = pd.read_excel(
                file_path,
                dtype=str
            )

        except Exception as e:

            raise CommandError(
                f"Unable to open Excel file: {e}"
            )
        df = df.loc[
            :,
            ~df.columns.astype(str).str.startswith("Unnamed:")
        ]

        # ==========================================
        # Required Columns
        # ==========================================

        required_columns = [
            "username",
            "family",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise CommandError(
                "Excel file is missing required columns: "
                + ", ".join(missing_columns)
            )

        # ==========================================
        # Exams
        # ==========================================

        exams = {}

        for exam_name in [
            "الترم الاول",
            "الترم الثاني",
            "الترم الثالث",
        ]:

            exam = (
                Exam.objects
                .filter(
                    name=exam_name,
                    year=academic_year
                )
                .first()
            )

            if not exam:

                raise CommandError(
                    f'Exam "{exam_name}" '
                    f'for year "{academic_year}" '
                    f'does not exist.'
                )

            exams[exam_name] = exam

        # ==========================================
        # Excel Columns Mapping
        # ==========================================
        #
        # Excel Column
        #       ↓
        # Subject
        #       ↓
        # Exam
        #
        # ==========================================

        columns_mapping = {

            # ======================================
            # الألحان
            # ======================================

            "الالحان الترم الأول": {
                "subject": "الالحان",
                "exam": "الترم الاول",
            },

            "الالحان الترم الثاني": {
                "subject": "الالحان",
                "exam": "الترم الثاني",
            },

            "الالحان الترم الثالث": {
                "subject": "الالحان",
                "exam": "الترم الثالث",
            },

            # ======================================
            # الطقس
            # ======================================

            "الطقس الترم الأول": {
                "subject": "الطقس",
                "exam": "الترم الاول",
            },

            # ======================================
            # القبطي
            # ======================================

            "القبطي الترم الثاني": {
                "subject": "القبطي",
                "exam": "الترم الثاني",
            },

            # ======================================
            # الكتاب المقدس
            # ======================================

            "الكتاب المقدس الترم الثالث": {
                "subject": "الكتاب المقدس",
                "exam": "الترم الثالث",
            },

            # ======================================
            # المحفوظات
            # ======================================

            "المحفوظات الترم الأول": {
                "subject": "المحفوظات",
                "exam": "الترم الاول",
            },

            "المحفوظات الترم الثاني": {
                "subject": "المحفوظات",
                "exam": "الترم الثاني",
            },

            "المحفوظات الترم الثالث": {
                "subject": "المحفوظات",
                "exam": "الترم الثالث",
            },

            # ======================================
            # الحضور والغياب
            # ======================================

            "الحضور والغياب الترم الأول": {
                "subject": "الحضور والغياب",
                "exam": "الترم الاول",
            },

            "الحضور والغياب الترم الثاني": {
                "subject": "الحضور والغياب",
                "exam": "الترم الثاني",
            },

            "الحضور والغياب الترم الثالث": {
                "subject": "الحضور والغياب",
                "exam": "الترم الثالث",
            },
        }

        # ==========================================
        # Normalize Mapping
        # ==========================================

        normalized_mapping = {}

        for column_name, config in columns_mapping.items():

            normalized_mapping[
                normalize(column_name)
            ] = config

        # ==========================================
        # Resolve SubjectExams
        # ==========================================

        column_subject_exams = {}

        for column in df.columns:

            # --------------------------------------
            # Columns that are not grades
            # --------------------------------------

            if column in {
                "username",
                "family",
            }:
                continue

            # --------------------------------------
            # Ignore unknown columns
            # --------------------------------------

            normalized_column = normalize(column)

            if normalized_column not in normalized_mapping:
                continue

            config = normalized_mapping[
                normalized_column
            ]

            subject_name = config["subject"]
            exam_name = config["exam"]

            # --------------------------------------
            # Find Subject
            # --------------------------------------

            subject = None

            normalized_subject_name = normalize(subject_name)

            for candidate in Subject.objects.all():

                if normalize(candidate.name) == normalized_subject_name:
                    subject = candidate
                    break

            if not subject:

                raise CommandError(
                    f'Column "{column}": '
                    f'Subject "{subject_name}" '
                    f'does not exist.'
                )

            # --------------------------------------
            # Find SubjectExam
            # --------------------------------------

            subject_exam = (
                SubjectExam.objects
                .filter(
                    subject=subject,
                    exam=exams[exam_name]
                )
                .first()
            )

            if not subject_exam:

                raise CommandError(
                    f'Column "{column}": '
                    f'SubjectExam for '
                    f'"{subject_name}" - '
                    f'"{exam_name}" '
                    f'does not exist.'
                )

            column_subject_exams[column] = subject_exam

        # ==========================================
        # Students
        # ==========================================

        imported_students = 0
        imported_results = 0
        skipped_results = 0

        # ==========================================
        # Process Excel Rows
        # ==========================================

        for index, row in df.iterrows():

            excel_row = index + 2

            # ======================================
            # Username
            # ======================================

            username = clean(
                row.get("username")
            )

            if not username:

                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: "
                        f"username مطلوب"
                    )
                )

                continue

            # ======================================
            # Family Name
            # ======================================

            family_name = clean(
                row.get("family")
            )

            if not family_name:

                raise CommandError(
                    f"Row {excel_row}: "
                    f"family مطلوب."
                )

            # ======================================
            # Find Student
            # ======================================

            student = (
                CustomUser.objects
                .filter(
                    username=username
                )
                .first()
            )

            if not student:

                raise CommandError(
                    f'Row {excel_row}: '
                    f'Student "{username}" '
                    f'was not found.'
                )

            # ======================================
            # Find Family
            # ======================================

            family = (
                Family.objects
                .annotate(
                    clean_name=Trim("name")
                )
                .filter(
                    clean_name=family_name
                )
                .first()
            )

            if not family:

                raise CommandError(
                    f'Row {excel_row}: '
                    f'Family "{family_name}" '
                    f'was not found.'
                )

            # ======================================
            # Validate Student Family
            # ======================================

            if student.family_id != family.id:

                actual_family = (
                    student.family.name
                    if student.family
                    else "بدون أسرة"
                )

                raise CommandError(
                    f'Row {excel_row}: '
                    f'Student "{username}" belongs to '
                    f'"{actual_family}", '
                    f'but Excel says '
                    f'"{family_name}".'
                )

            # ======================================
            # Enrollment
            # ======================================

            enrollment, _ = (
                StudentEnrollment.objects
                .get_or_create(
                    student=student,
                    family=family,
                    academic_year=academic_year
                )
            )

            imported_students += 1

            student_results = 0

            # ======================================
            # Results
            # ======================================

            for column, subject_exam in (
                column_subject_exams.items()
            ):

                value = clean(
                    row.get(column)
                )

                # ----------------------------------
                # Empty Grade
                # ----------------------------------

                if value is None:

                    skipped_results += 1

                    continue

                # ----------------------------------
                # Convert Grade
                # ----------------------------------

                try:

                    points = float(value)

                except (ValueError, TypeError):

                    raise CommandError(
                        f'Row {excel_row}: '
                        f'Invalid grade "{value}" '
                        f'in column "{column}".'
                    )

                # ----------------------------------
                # Negative Grade
                # ----------------------------------

                if points < 0:

                    raise CommandError(
                        f'Row {excel_row}: '
                        f'Grade for "{column}" '
                        f'cannot be negative.'
                    )

                # ----------------------------------
                # Max Grade Validation
                # ----------------------------------

                if points > subject_exam.max_grade:

                    raise CommandError(
                        f'Row {excel_row}: '
                        f'Grade {points} for '
                        f'"{column}" exceeds '
                        f'max grade '
                        f'{subject_exam.max_grade}.'
                    )

                # ----------------------------------
                # Create / Update Result
                # ----------------------------------

                Result.objects.update_or_create(
                    enrollment=enrollment,
                    subject_exam=subject_exam,
                    defaults={
                        "points": points
                    }
                )

                imported_results += 1
                student_results += 1

            # ======================================
            # Calculate Annual Status
            # ======================================

            from results.services import (
                update_annual_status
            )

            update_annual_status(
                enrollment
            )

            # ======================================
            # Log
            # ======================================

            self.stdout.write(
                f"Row {excel_row}: "
                f"{username} -> "
                f"{student_results} results"
            )

        # ==========================================
        # Done
        # ==========================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Import completed successfully."
            )
        )

        self.stdout.write(
            f"Students imported: "
            f"{imported_students}"
        )

        self.stdout.write(
            f"Results imported/updated: "
            f"{imported_results}"
        )

        self.stdout.write(
            f"Empty grades skipped: "
            f"{skipped_results}"
        )