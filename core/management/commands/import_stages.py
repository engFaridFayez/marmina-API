from django.core.management.base import BaseCommand
import pandas as pd

from stages.models import Stage
from users.models import CustomUser


class Command(BaseCommand):
    help = "Import stages from Excel"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **kwargs):
        df = pd.read_excel(kwargs["file"])

        created = 0

        for i, row in df.iterrows():
            name = row.get("name")
            leader_username = row.get("leader_username")

            if not name or pd.isna(name):
                self.stdout.write(
                    self.style.WARNING(f"Row {i} skipped")
                )
                continue

            stage, created_flag = Stage.objects.get_or_create(
                name=name
            )

            # لو فيه username للأمين
            if leader_username and not pd.isna(leader_username):

                try:
                    leader = CustomUser.objects.get(
                        username=leader_username
                    )

                    stage.leaders.add(leader)

                except CustomUser.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Leader '{leader_username}' not found in row {i}"
                        )
                    )

            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} stages")
        )