from django.core.management.base import BaseCommand
import pandas as pd
from django.contrib.auth import get_user_model

from stages.models import Stage, Family

User = get_user_model()


class Command(BaseCommand):
    help = "Import users from Excel"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **kwargs):
        df = pd.read_excel(kwargs['file'])

        created = 0

        for i, row in df.iterrows():
            username = row.get('username')
            password = row.get('password')
            role = row.get('role')
            full_name = row.get('full_name')
            phone = row.get('phone')


            stage_name = row.get('stage')
            family_name = row.get('family')

            if not username or not password or not role:
                self.stdout.write(self.style.WARNING(f"Row {i} skipped"))
                continue

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"{username} exists"))
                continue

            stage = None
            family = None

            # ✅ get stage
            if pd.notna(stage_name):
                stage = Stage.objects.filter(name=stage_name).first()

            # ✅ get family
            if pd.notna(family_name):
                family = Family.objects.filter(name=family_name).first()

            # 🔥 validation حسب role
            if role in ["مخدوم", "خادم عادي", "امين اسرة"] and not family:
                self.stdout.write(self.style.WARNING(f"Row {i} لازم family"))
                continue

            if role == "امين مرحلة" and not stage:
                self.stdout.write(self.style.WARNING(f"Row {i} لازم stage"))
                continue

            user = User.objects.create_user(
                username=username,
                password=password,
                role=role,
                full_name=full_name,
                phone=phone,
                family=family
            )

            # 🔥 ربط أمين المرحلة
            if role == "امين مرحلة":
                stage.leader = user
                stage.save()

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} users"))