from django.core.management.base import BaseCommand

from forecasts.utils.constants import MODEL_FILE_MAPPING
from forecasts.utils.csv_utils import import_data, read_csv_file


class Command(BaseCommand):
    """Management command to fill the database with data from CSV files."""

    help = "Fill database with data."

    def handle(self, *args, **options):
        """Command handler."""
        for model, data in MODEL_FILE_MAPPING.items():
            try:
                csv_data = read_csv_file(data["path"])
                import_data(model, csv_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{model.__name__} data successfully imported!",
                    )
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to import data:{e}")
                )
