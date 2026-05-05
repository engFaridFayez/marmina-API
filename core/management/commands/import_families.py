from django.core.management.base import BaseCommand
import pandas as pd
from stages.models import Stage, Family


class Command(BaseCommand):
    help = "Import families from Excel"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **kwargs):
        df = pd.read_excel(kwargs['file'])

        created = 0

        for i, row in df.iterrows():
            name = row.get('name')
            year = row.get('year')
            stage_name = row.get('stage')

            if not name or not stage_name:
                self.stdout.write(self.style.WARNING(f"Row {i} skipped"))
                continue

            try:
                stage = Stage.objects.get(name=stage_name)
            except Stage.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Stage not found: {stage_name}"))
                continue

            _, created_flag = Family.objects.get_or_create(
                name=name,
                stage=stage,
                defaults={"year": year}
            )

            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} families"))