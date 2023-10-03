import json
from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from pandas import json_normalize
from rest_framework import status
from rest_framework.response import Response

from forecasts import models


def generate_forecast_report(validated_data):
    """Generate a forecast report based on validated data."""
    try:
        stores = get_stores(validated_data)
        skus = get_skus(validated_data)
        forecasts = get_forecasts(stores, skus)

        if forecasts:
            return generate_excel_report(forecasts, skus, stores)
        return Response(
            {"error": "Forecasts does not exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response(
            {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


def generate_excel_report(forecasts, skus, stores):
    """Generate an Excel report based on forecast, SKU, and store data."""
    stores_df = get_dataframe(stores)
    skus_df = get_dataframe(skus)
    forecasts_df = get_dataframe(forecasts)

    cleared_data = clear_report_data(forecasts_df, skus_df, stores_df)

    with BytesIO() as excel_buffer:
        try:
            cleared_data.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            excel_response = HttpResponse(
                excel_buffer.read(),
                content_type=(
                    "application/vnd.openxmlformats-officedocument"
                    ".spreadsheetml.sheet"
                ),
            )
            excel_response[
                "Content-Disposition"
            ] = "attachment; filename=merged_data.xlsx"
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return excel_response


def clear_forecast_dataframe(forecasts_df):
    """Clear the forecast DataFrame by processing date fields."""
    forecasts_df["forecast_date"] = pd.to_datetime(
        forecasts_df["forecast_date"]
    ).dt.tz_localize(None)

    forecasts_df_expanded = json_normalize(
        forecasts_df["forecast"].apply(json.loads)
    )

    forecasts_df = forecasts_df.drop(columns=["id"])

    merged_df = pd.concat([forecasts_df, forecasts_df_expanded], axis=1)

    return merged_df.drop(columns=["forecast"])


def merge_on_columns(left_df, right_df, left_on, right_on, how="inner"):
    """Merge two DataFrames on specified columns."""
    merged_df = pd.merge(
        left_df, right_df, left_on=left_on, right_on=right_on, how=how
    )
    return merged_df.drop(columns=[left_on, right_on])


def clear_report_data(forecasts_df, skus_df, stores_df):
    """Prepare and cleans data for generating an Excel report."""
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
