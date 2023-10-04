from forecasts import models

MODEL_FILE_MAPPING = {
    models.Store: {
        "path": "../data/st_df.csv",
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
    models.SKU: {
        "path": "../data/pr_df.csv",
        "mapping": {
            "group": {"csv_name": "pr_group_id"},
            "category": {"csv_name": "pr_cat_id"},
            "subcategory": {"csv_name": "pr_subcat_id"},
            "sku": {"csv_name": "pr_sku_id"},
            "uom": {"csv_name": "pr_uom_id"},
        },
    },
    models.Sale: {
        "path": "../data/sales_df_train.csv",
        "mapping": {
            "store": {"csv_name": "st_id", "reference": models.Store},
            "sku": {"csv_name": "pr_sku_id", "reference": models.SKU},
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
    models.Forecast: {
        "path": "../data/forecasts.csv",
        "mapping": {
            "store": {"csv_name": "st_id", "reference": models.Store},
            "sku": {"csv_name": "pr_sku_id", "reference": models.SKU},
            "forecast": {"csv_name": "forecast"},
        },
    },
}
