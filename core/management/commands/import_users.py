from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
import pandas as pd

from users.models import CustomUser  # عدل حسب اسم الابلكيشن

class Command(BaseCommand):
    help = "Import users from Excel file"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))
            return

        roles_choices = [choice[0] for choice in CustomUser._meta.get_field('role').choices]

        created_count = 0

        for index, row in df.iterrows():
            username = row.get('username')
            password = row.get('password')
            role = row.get('role')

            # ✅ Validation
            if not username or not password or not role:
                self.stdout.write(self.style.WARNING(f"Row {index} skipped (missing data)"))
                continue

            if role not in roles_choices:
                self.stdout.write(self.style.WARNING(f"Row {index} skipped (invalid role: {role})"))
                continue

            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User {username} already exists"))
                continue

            # ✅ Create user
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                role=role
            )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} users"))