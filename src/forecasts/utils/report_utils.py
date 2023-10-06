import json
from datetime import date, datetime
from io import BytesIO

import pandas as pd
from django.core.files.base import ContentFile
from django.db import transaction
from pandas import json_normalize
from rest_framework import status

from forecasts import models
from forecasts.errors import ReportGenerationError
from forecasts.models import AsyncFileResults


def generate_forecast_report(validated_data):
    """Generate a forecast report based on validated data."""
    stores = get_stores(validated_data)
    skus = get_skus(validated_data)
    forecasts = get_forecasts(stores, skus)
    if forecasts:
        return generate_excel_report(
            forecasts,
            skus,
            stores,
            validated_data.get("from_date"),
            validated_data.get("to_date"),
        )
    raise ReportGenerationError(
        message="No forecasts found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


def get_stores(validated_data):
    """Retrieve stores based on the validated data."""
    return models.Store.objects.filter(
        id__in=validated_data.get("store_ids"),
    )


def get_skus(validated_data):
    """Retrieve SKUs based on the validated data."""
    filters = {"group__in": validated_data.get("groups")}

    if categories := validated_data.get("categories"):
        filters["category__in"] = categories

    if subcategories := validated_data.get("subcategories"):
        filters["subcategory__in"] = subcategories

    if sku_ids := validated_data.get("sku_ids"):
        filters["id__in"] = sku_ids

    return models.SKU.objects.filter(**filters)


def get_forecasts(stores, skus):
    """Retrieve forecasts based on stores and SKUs."""
    return models.Forecast.objects.filter(
        forecast_date__date=date.today(),
        store__in=stores,
        sku__in=skus,
    )


def get_verbose_names(*models):
    """Get verbose names for fields in the specified models."""
    names = {}
    for model in models:
        meta = model._meta
        names.update(
            {
                field.name: meta.get_field(field.name).verbose_name
                for field in meta.fields
            }
        )
    return names


def get_dataframe(queryset):
    """Convert a queryset to a pandas DataFrame."""
    return pd.DataFrame(list(queryset.values()))


def generate_excel_report(forecasts, skus, stores, from_date, to_date):
    """Generate an Excel report based on forecast, SKU, and store data."""
    stores_df = get_dataframe(stores)
    skus_df = get_dataframe(skus)
    forecasts_df = get_dataframe(forecasts)

    cleared_data = clear_report_data(
        forecasts_df, skus_df, stores_df, from_date, to_date
    )

    excel_buffer = BytesIO()
    cleared_data.to_excel(
        excel_buffer,
        index=False,
        engine="openpyxl",
    )
    excel_buffer.seek(0)

    return excel_buffer.getvalue()


def clear_forecast_dataframe(forecasts_df, from_date=None, to_date=None):
    """Clear the forecast DataFrame by processing date fields."""
    forecasts_df["forecast_date"] = pd.to_datetime(
        forecasts_df["forecast_date"],
    ).dt.tz_localize(None)

    forecasts_df_expanded = json_normalize(
        forecasts_df["forecast"].apply(json.loads),
    )

    if from_date or to_date:
        forecasts_df = filter_by_date(forecasts_df, from_date, to_date)

    forecasts_df = forecasts_df.drop(columns=["id"])

    merged_df = pd.concat([forecasts_df, forecasts_df_expanded], axis=1)

    return merged_df.drop(columns=["forecast"])


def merge_on_columns(left_df, right_df, left_on, right_on, how="inner"):
    """Merge two DataFrames on specified columns."""
    merged_df = pd.merge(
        left_df,
        right_df,
        left_on=left_on,
        right_on=right_on,
        how=how,
    )
    return merged_df.drop(columns=[left_on, right_on])


def clear_report_data(forecasts_df, skus_df, stores_df, from_date, to_date):
    """Prepare and cleans data for generating an Excel report."""
    verbose_names = get_verbose_names(
        models.SKU,
        models.Forecast,
        models.Store,
    )
    forecasts_df = clear_forecast_dataframe(forecasts_df, from_date, to_date)
    merged_df = merge_on_columns(skus_df, forecasts_df, "id", "sku_id")
    merged_df = merge_on_columns(stores_df, merged_df, "id", "store_id")
    merged_df.rename(columns=verbose_names, inplace=True)
    return merged_df


def filter_by_date(dataframe, from_date, to_date):
    """Filer report columns by date."""
    selected_columns = [
        col
        for col in dataframe.columns
        if from_date <= datetime.strptime(col, "%Y-%m-%d").date() <= to_date
    ]
    selected_columns.sort()

    return dataframe[selected_columns]


def get_existing_report(user_id, data):
    """Retrieve an existing report from the database."""
    return AsyncFileResults.objects.filter(
        user_id=user_id,
        filters=json.dumps(data, default=serialize_date),
        created_at=date.today(),
        errors=None,
    ).first()


def generate_report_content(data):
    """Generate the content for the report."""
    result, errors = None, None
    try:
        result = ContentFile(
            generate_forecast_report(data),
            name=f"forecast_report_on_{date.today()}.xlsx",
        )
    except ReportGenerationError as report_exc:
        errors = {
            "status": report_exc.status_code,
            "data": {"error": str(report_exc)},
        }
    except Exception as ex:
        errors = {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "data": {"error": str(ex)},
        }

    return result, errors


def save_report_to_database(user_id, task_id, data, result, errors):
    """Save the generated report to the database."""
    with transaction.atomic():
        AsyncFileResults.objects.create(
            user_id=user_id,
            task_id=task_id,
            filters=json.dumps(data, default=serialize_date),
            result=result,
            errors=json.dumps(errors),
        )


def serialize_date(obj):
    """Serialize a date object to its ISO format."""
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type not serializable")
