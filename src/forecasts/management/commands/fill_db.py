import csv
from itertools import islice

from django.core.management.base import BaseCommand
from tqdm import tqdm

from forecasts.models import SKU, Sale, Store


class Command(BaseCommand):
    """Management command to fill the database with data from CSV files."""

    BATCH_SIZE = 1000

    PROGRESS_BAR_CONFIG = {"ncols": 100, "colour": "green"}

    help = "Fill database with data."
    model_file_mapping = {
        Store: {
            "path": "data/st_df.csv",
            "mapping": {
                "store": {"csv_name": "st_id"},
                "city": {"csv_name": "st_city_id"},
                "division": {"csv_name": "st_division_code"},
                "type_format": {"csv_name": "st_type_format_id"},
                "loc": {"csv_name": "st_type_loc_id"},
                "size": {"csv_name": "st_type_size_id"},
                "is_active": {"csv_name": "st_is_active"},
            },
        },
        SKU: {
            "path": "data/pr_df.csv",
            "mapping": {
                "group": {"csv_name": "pr_group_id"},
                "category": {"csv_name": "pr_cat_id"},
                "subcategory": {"csv_name": "pr_subcat_id"},
                "sku": {"csv_name": "pr_sku_id"},
                "uom": {"csv_name": "pr_uom_id"},
            },
        },
        Sale: {
            "path": "data/sales_df_train.csv",
            "mapping": {
                "store": {"csv_name": "st_id", "reference": Store},
                "sku": {"csv_name": "pr_sku_id", "reference": SKU},
                "date": {"csv_name": "date"},
                "sales_type": {"csv_name": "pr_sales_type_id", "type": float},
                "sales_units": {
                    "csv_name": "pr_sales_in_units",
                    "type": float,
                },
                "sales_units_promo": {
                    "csv_name": "pr_promo_sales_in_units",
                    "type": float,
                },
                "sales_rub": {"csv_name": "pr_sales_in_rub", "type": float},
                "sales_rub_promo": {
                    "csv_name": "pr_promo_sales_in_rub",
                    "type": float,
                },
            },
        },
    }

    def handle(self, *args, **options):
        """Command handler."""
        for model, data in self.model_file_mapping.items():
            self.import_data(model, **data)

    def read_csv_file(self, file_path, batch_size=None):
        """Open a CSV file."""
        if batch_size is None:
            batch_size = self.BATCH_SIZE
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            while True:
                batch = list(islice(csv_reader, batch_size))
                if not batch:
                    return

                yield batch

    def import_data(self, model, path, mapping):
        """Open a CSV file and populate the database with related models."""
        try:
            for batch in tqdm(
                self.read_csv_file(path),
                desc=f"Filling {model.__name__} table...",
                **self.PROGRESS_BAR_CONFIG,
            ):
                objects = []
                for row in batch:
                    object_data = {}
                    for field, data in mapping.items():
                        if referenced_model := data.get("reference", None):
                            referenced_model_instance = (
                                referenced_model.objects.get(
                                    **{field: row[data["csv_name"]]},
                                )
                            )
                            object_data[field] = referenced_model_instance
                        elif field_type := data.get("type", None):
                            object_data[field] = field_type(
                                row[data["csv_name"]],
                            )
                        else:
                            object_data[field] = row[data["csv_name"]]
                    objects.append(model(**object_data))
                model.objects.bulk_create(objects, batch_size=self.BATCH_SIZE)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{model.__name__} data successfully imported!",
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to import data:{e}"))
