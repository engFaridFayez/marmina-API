import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from api import settings
from stages.models import Stage, Family, Children, Servant

EXCEL_FILE = os.path.join(settings.BASE_DIR, 'stages', 'data')

EXCEL_FILE_PATH = os.path.join(EXCEL_FILE,'data6.xlsx')

def import_data():
    # Read Excel
    xls = pd.ExcelFile(EXCEL_FILE_PATH)

    stages_df = pd.read_excel(xls, 'Stage')
    for _, row in stages_df.iterrows():
        Stage.objects.get_or_create(name=row['name'])

    families_df = pd.read_excel(xls, 'Family')
    for _, row in families_df.iterrows():
        try:
            stage = Stage.objects.get(name=row['stage_id'])
            Family.objects.get_or_create(
                name=row['name'],
                year=row['year'],
                stage=stage
            )
        except Stage.DoesNotExist:
            print(f"Stage {row['stage_id']} not found for family {row['name']}")

    children_df = pd.read_excel(xls, 'Children')
    for _, row in children_df.iterrows():
        try:
            family = Family.objects.get(name=row['family_id'])
            Children.objects.create(
                name=row['name'],
                birth_date=row['birth_date'],
                phone=row['phone'],
                parent_phone=row['parent_phone'],
                address=row['address'],
                father=row['father'],
                year_of_entrance=row['year_of_entrance'],
                year_of_graduation=row['year_of_graduation'],
                family=family
            )
        except Family.DoesNotExist:
            print(f"Family {row['family_id']} not found for child {row['name']}")
        except IntegrityError as e:
            print(f"Error creating child {row['name']}: {e}")

        # Import Servants (lookup Stage and Family, optional)
    if 'Servant' in xls.sheet_names:
        servants_df = pd.read_excel(xls, 'Servant')
        for _, row in servants_df.iterrows():
            stage = Stage.objects.filter(name=row['stage_id']).first() if pd.notna(row['stage_id']) else None
            family = Family.objects.filter(name=row['family_id']).first() if pd.notna(row['family_id']) else None
            Servant.objects.create(
                name=row['name'],
                birth_date=row['birth_date'],
                address=row['address'],
                role=row['role'],
                stage=stage,
                family=family
            )

    print("Import completed.")

import_data()

class Command(BaseCommand):
    help = "Import seed data from Excel file into database"

    def handle(self, *args, **kwargs):
        if not os.path.exists(EXCEL_FILE_PATH):
            self.stdout.write(self.style.ERROR(f"File not found: {EXCEL_FILE_PATH}"))
            return

        import_data()
        self.stdout.write(self.style.SUCCESS("Seed data imported successfully."))
    