import csv
from io import TextIOWrapper
from itertools import islice

from tqdm import tqdm

from forecasts.utils.constants import MODEL_FILE_MAPPING


def read_csv_file(data_source, batch_size=1000):
    """Read CSV data from either a file or bytes."""

    def read_csv_from_io(io_obj):
        with io_obj as data:
            csv_reader = csv.DictReader(data)
            while True:
                batch = list(islice(csv_reader, batch_size))
                if not batch:
                    return
                yield batch

    if isinstance(data_source, str):
        with open(data_source, "r") as file:
            yield from read_csv_from_io(file)
    else:
        byte_stream = TextIOWrapper(data_source, encoding="utf-8")
        yield from read_csv_from_io(byte_stream)


def import_data(model, data):
    """Populate the database with related models."""
    model_mapping = MODEL_FILE_MAPPING[model]["mapping"]

    for batch in tqdm(
        data,
        desc=f"Filling {model.__name__} table...",
        ncols=100,
        colour="green",
    ):
        objects = create_objects(model, model_mapping, batch)
        model.objects.bulk_create(objects, ignore_conflicts=True)


def create_objects(model, model_mapping, batch):
    """Create database objects from batch data."""
    objects = []

    for row in batch:
        object_data = {}
        try:
            for field, data in model_mapping.items():
                object_data[field] = process_field_data(row, field, data)
        except Exception:
            pass
        else:
            if all(object_data.keys()):
                objects.append(model(**object_data))
    return objects


def process_field_data(row, field, data):
    """Process field data based on mapping information."""
    field_value = row.get(data["csv_name"], None)

    if referenced_model := data.get("reference", None):
        return referenced_model.objects.get(**{field: field_value})
    elif field_type := data.get("type", None):
        return field_type(field_value)
    else:
        return field_value
