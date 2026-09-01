from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models.functions import Trim
import pandas as pd

from stages.models import Stage, Family
from users.models import StageLeader

User = get_user_model()


class Command(BaseCommand):
    help = "Import users from Excel"
    
    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **kwargs):
        df = pd.read_excel(kwargs["file"], dtype=str)
        
        created = 0

        def clean(value):
            if pd.isna(value):
                return None
            if isinstance(value, str):
                value = value.strip()
                return value if value else None
            return value

        def parse_date(value):
            value = clean(value)
            if value is None:
                return None
            return pd.to_datetime(value, dayfirst=True).date()

        for index, row in df.iterrows():

            username = clean(row.get("username"))
            password = clean(row.get("password"))
            role = clean(row.get("role"))

            if not username or not password or not role:
                self.stdout.write(
                    self.style.WARNING(f"Row {index + 2}: username/password/role مطلوبين")
                )
                continue

            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f"{username} موجود بالفعل")
                )
                continue

            stage = None
            family = None

            stage_name = clean(row.get("stage"))
            family_name = clean(row.get("family"))

            if stage_name:
                stage = (
                        Stage.objects
                        .annotate(clean_name=Trim("name"))
                        .filter(clean_name=stage_name)
                        .first()
                    )
                if not stage:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Row {index + 2}: المرحلة '{stage_name}' غير موجودة"
                        )
                    )

            if family_name:
                family = (
                        Family.objects
                        .annotate(clean_name=Trim("name"))
                        .filter(clean_name=family_name)
                        .first()
                    )
                if not family:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Row {index + 2}: الأسرة '{family_name}' غير موجودة"
                        )
                    )

            # Validation

            if role in ["مخدوم", "خادم", "امين اسرة", "امين مساعد اسرة"] and not family:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {index + 2}: هذا المستخدم يجب أن يكون له أسرة"
                    )
                )
                continue

            if role == "امين مرحلة" and not stage:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {index + 2}: أمين المرحلة يجب أن يكون له مرحلة"
                    )
                )
                continue

            user = User.objects.create_user(
                username=username,
                password=password,
                full_name=clean(row.get("full_name")) or "",
                address=clean(row.get("address")) or "",
                phone=clean(row.get("phone")) or "",
                whatsapp=clean(row.get("whatsapp")),
                parent_phone=clean(row.get("parent_phone")),
                father=clean(row.get("father")) or "",
                joined_date=parse_date(row.get("joined_date")),
                birth_date=parse_date(row.get("birth_date")),
                role=role,
                slogan=clean(row.get("slogan")) or "شاطر",
                family=family,
            )

            # ربط أمين المرحلة
            if role == "امين مرحلة":
                StageLeader.objects.get_or_create(
                    stage=stage,
                    customuser=user,
                )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {created} users.")
        )