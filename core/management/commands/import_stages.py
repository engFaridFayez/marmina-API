from django.core.management.base import BaseCommand
import pandas as pd
from stages.models import Stage


class Command(BaseCommand):
    help = "Import stages from Excel"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **kwargs):
        df = pd.read_excel(kwargs['file'])

        created = 0

        for i, row in df.iterrows():
            name = row.get('name')

            if not name or pd.isna(name):
                self.stdout.write(self.style.WARNING(f"Row {i} skipped"))
                continue

            _, created_flag = Stage.objects.get_or_create(name=name)

            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} stages"))