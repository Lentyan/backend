import json
from datetime import date
from io import BytesIO

import pandas as pd
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import status

from api.v1 import filters
from forecasts import models
from forecasts.errors import ReportGenerationError
from forecasts.models import AsyncFileResults


def generate_forecast_report(validated_data):
    """Generate a forecast report based on validated data."""
    stores = get_stores(validated_data)
    skus = get_skus(validated_data)
    forecasts = get_forecasts(validated_data, skus)
    if forecasts:
        forecast_report_date = clear_forecast_report_data(
            forecasts,
            skus,
            stores,
        )
        return generate_excel_report(forecast_report_date)
    raise ReportGenerationError(
        message="No forecasts found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


def generate_statistics_report(validated_data):
    """Generate a statistic report based on validated data."""
    skus = get_skus(validated_data)
    forecasts_queryset = get_forecasts(validated_data, skus)
    sales_queryset = get_sales(validated_data, skus)
    if not forecasts_queryset.exists():
        raise ReportGenerationError(
            "Forecasts not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if not sales_queryset.exists():
        raise ReportGenerationError(
            "Sales data not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    statistics_data = clear_statistic_data(
        forecasts_queryset,
        sales_queryset,
    )
    return generate_excel_report(statistics_data)


def get_statistics_data(request):
    """Return statistics data."""
    forecasts_queryset = filters.ForecastFilter(
        request.GET,
        models.Forecast.objects.all(),
    ).qs
    sales_queryset = filters.SaleFilter(
        request.GET, models.Sale.objects.all()
    ).qs

    if not forecasts_queryset.exists():
        raise ReportGenerationError(
            "Forecasts not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if not sales_queryset.exists():
        raise ReportGenerationError(
            "Sales data not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    statistics_content = clear_statistic_data(
        forecasts_queryset,
        sales_queryset,
    )
    return statistics_content


def clear_statistic_data(forecasts_queryset, sales_queryset):
    """Clear statistics data."""
    forecasts_df = (
        get_dataframe(forecasts_queryset)
        .groupby(
            ["store_id", "sku_id"],
            as_index=False,
        )["target"]
        .sum()
    )

    sales_df = (
        get_dataframe(sales_queryset)
        .groupby(["store_id", "sku_id"], as_index=False)
        .agg(
            {
                "sales_units": "sum",
                "sales_units_promo": "sum",
                "sales_rub": "sum",
                "sales_rub_promo": "sum",
            }
        )
    )

    sales_df["price"] = sales_df["sales_rub"] / sales_df[
        "sales_units"
    ].replace(0, 1)

    merged_df = pd.merge(
        forecasts_df,
        sales_df,
        on=["store_id", "sku_id"],
        how="inner",
    )

    merged_df["quantity_difference"] = (
        merged_df["sales_units"] - merged_df["target"]
    )
    merged_df["amount_difference"] = merged_df[
        "quantity_difference"
    ] * merged_df["price"].astype(float)
    merged_df["WAPE"] = (
        merged_df["quantity_difference"] / merged_df["sales_units"]
    )
    return merged_df


def get_sales(validated_data, skus):
    """Retrieve sales based on the validated data."""
    return models.Sale.objects.prefetch_related("store_forecasts").filter(
        store_id__in=validated_data.get("store_ids"),
        sku_id__in=skus,
        date__gte=validated_data.get("from_date"),
        date__lte=validated_data.get("to_date"),
    )


def get_stores(validated_data):
    """Retrieve stores based on the validated data."""
    return models.Store.objects.prefetch_related("store_forecasts").filter(
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

    if any(filters.values()):
        return models.SKU.objects.prefetch_related("sku_forecasts").filter(
            **filters
        )
    return models.SKU.objects.prefetch_related("sku_forecasts").all()


def get_forecasts(validated_data, skus):
    """Retrieve forecasts based on stores and SKUs."""
    return models.Forecast.objects.filter(
        forecast_date__date=validated_data.get("forecast_date"),
        date__gte=validated_data.get("from_date"),
        date__lte=validated_data.get("to_date"),
        store__in=validated_data.get("store_ids"),
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


def generate_excel_report(cleared_data):
    """Generate an Excel report based on forecast, SKU, and store data."""
    excel_buffer = BytesIO()
    cleared_data.to_excel(
        excel_buffer,
        index=False,
        engine="openpyxl",
    )
    excel_buffer.seek(0)

    return excel_buffer.getvalue()


def clear_forecast_dataframe(forecasts_df):
    """Clear the forecast DataFrame by processing date fields."""
    forecasts_df = forecasts_df.pivot_table(
        index=["sku_id", "store_id", "forecast_date"],
        columns="date",
        values="target",
        aggfunc="sum",
        fill_value=0,
    )

    forecasts_df.reset_index(inplace=True)
    forecasts_df["forecast_date"] = pd.to_datetime(
        forecasts_df["forecast_date"],
    ).dt.tz_localize(None)
    return forecasts_df


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


def clear_forecast_report_data(forecasts, skus, stores):
    """Prepare and cleans data for generating an Excel report."""
    stores_df = get_dataframe(stores)
    skus_df = get_dataframe(skus)
    forecasts_df = get_dataframe(forecasts)

    verbose_names = get_verbose_names(
        models.SKU,
        models.Forecast,
        models.Store,
    )
    forecasts_df = clear_forecast_dataframe(forecasts_df)
    merged_df = merge_on_columns(skus_df, forecasts_df, "id", "sku_id")
    merged_df = merge_on_columns(stores_df, merged_df, "id", "store_id")
    merged_df.rename(columns=verbose_names, inplace=True)
    return merged_df


def get_existing_report(user_id, data):
    """Retrieve an existing report from the database."""
    return AsyncFileResults.objects.filter(
        user_id=user_id,
        filters=json.dumps(data, default=serialize_date),
        created_at=date.today(),
        errors="null",
    ).first()


def generate_report_content(data, generator, name):
    """Generate the content for the report."""
    result, errors = None, None
    try:
        result = ContentFile(
            generator(data),
            name=name,
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
