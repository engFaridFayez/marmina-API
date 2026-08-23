from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.functions import Trim
import pandas as pd

from stages.models import Stage, Family


class Command(BaseCommand):
    help = "Import families from Excel"

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            type=str,
            help="Path to Excel file"
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):

        file_path = kwargs["file"]

        # ==========================================
        # Load Excel
        # ==========================================

        try:
            df = pd.read_excel(
                file_path,
                dtype=str
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Unable to open Excel file: {e}"
                )
            )
            return

        # ==========================================
        # Helpers
        # ==========================================

        def clean(value):
            if pd.isna(value):
                return None

            if isinstance(value, str):
                value = value.strip()
                return value if value else None

            return str(value).strip()

        # ==========================================
        # Validate Columns
        # ==========================================

        required_columns = [
            "name",
            "year",
            "stage",
            "next_family",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            self.stdout.write(
                self.style.ERROR(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )
            )
            return

        # ==========================================
        # First Pass
        # Create / Update Families
        # ==========================================

        imported = 0
        created = 0
        updated = 0
        skipped = 0

        # هنخزن بيانات next_family
        # علشان نعمل الربط في المرحلة الثانية
        family_data = []

        for index, row in df.iterrows():

            excel_row = index + 2

            name = clean(row.get("name"))
            year = clean(row.get("year"))
            stage_name = clean(row.get("stage"))
            next_family_name = clean(row.get("next_family"))

            # ======================================
            # Required fields
            # ======================================

            if not name:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: name مطلوب"
                    )
                )
                skipped += 1
                continue

            if not stage_name:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: stage مطلوب"
                    )
                )
                skipped += 1
                continue

            # ======================================
            # Find Stage
            # ======================================

            stage = (
                Stage.objects
                .annotate(clean_name=Trim("name"))
                .filter(clean_name=stage_name)
                .first()
            )

            if not stage:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: "
                        f"المرحلة '{stage_name}' غير موجودة"
                    )
                )
                skipped += 1
                continue

            # ======================================
            # Find Family
            # ======================================

            family = (
                Family.objects
                .annotate(clean_name=Trim("name"))
                .filter(
                    clean_name=name,
                    stage=stage
                )
                .first()
            )

            # ======================================
            # Create
            # ======================================

            if not family:

                family = Family.objects.create(
                    name=name,
                    year=year or "",
                    stage=stage
                )

                created += 1

            # ======================================
            # Update
            # ======================================

            else:

                changed = False

                if family.year != (year or ""):
                    family.year = year or ""
                    changed = True

                if family.stage_id != stage.id:
                    family.stage = stage
                    changed = True

                if changed:
                    family.save()
                    updated += 1

            imported += 1

            # ======================================
            # Store next_family data
            # ======================================

            family_data.append({
                "row": excel_row,
                "family": family,
                "next_family_name": next_family_name,
            })

        # ==========================================
        # Second Pass
        # Link next_family
        # ==========================================

        linked = 0
        cleared = 0

        for item in family_data:

            excel_row = item["row"]
            family = item["family"]
            next_family_name = item["next_family_name"]

            # ======================================
            # No next family
            # ======================================

            if not next_family_name:

                if family.next_family_id is not None:

                    family.next_family = None

                    family.save(
                        update_fields=["next_family"]
                    )

                    cleared += 1

                continue

            # ======================================
            # Find next family
            #
            # IMPORTANT:
            # next_family can belong to another stage.
            #
            # Example:
            #
            # Stage 1
            # Family 3
            #      ↓
            # Stage 2
            # Family 4
            #
            # Therefore we DO NOT filter by stage.
            # ======================================

            next_family = (
                Family.objects
                .annotate(clean_name=Trim("name"))
                .filter(
                    clean_name=next_family_name
                )
                .first()
            )

            if not next_family:

                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: "
                        f"الأسرة التالية '{next_family_name}' "
                        f"غير موجودة"
                    )
                )

                continue

            # ======================================
            # Prevent self-reference
            # ======================================

            if next_family.id == family.id:

                self.stdout.write(
                    self.style.WARNING(
                        f"Row {excel_row}: "
                        f"الأسرة '{family.name}' "
                        f"لا يمكن أن تكون next_family لنفسها"
                    )
                )

                continue

            # ======================================
            # Update next_family
            # ======================================

            if family.next_family_id != next_family.id:

                family.next_family = next_family

                family.save(
                    update_fields=["next_family"]
                )

                linked += 1

        # ==========================================
        # Done
        # ==========================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Families import completed successfully."
            )
        )

        self.stdout.write(
            f"Families processed: {imported}"
        )

        self.stdout.write(
            f"Families created: {created}"
        )

        self.stdout.write(
            f"Families updated: {updated}"
        )

        self.stdout.write(
            f"Next families linked: {linked}"
        )

        self.stdout.write(
            f"Next families cleared: {cleared}"
        )

        self.stdout.write(
            f"Rows skipped: {skipped}"
        )