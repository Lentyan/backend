from rest_framework import serializers

from forecasts.models import SKU, Forecast, Sale, Store


class SKUSerializer(serializers.ModelSerializer):
    """SKU model serializer."""

    class Meta:
        """SKU model serializer meta."""

        model = SKU
        fields = (
            "sku",
            "group",
            "category",
            "subcategory",
            "uom",
        )


class StoreSerializer(serializers.ModelSerializer):
    """Store model serializer."""

    class Meta:
        """Store model serializer meta."""

        model = Store
        fields = (
            "store",
            "city",
            "division",
            "type_format",
            "loc",
            "size",
            "is_active",
        )


class SaleSerializer(serializers.ModelSerializer):
    """Sale model serializer."""

    class Meta:
        """Sale model serializer meta."""

        model = Sale
        fields = (
            "date",
            "sales_type",
            "sales_units",
            "sales_units_promo",
            "sales_rub",
            "sales_rub_promo",
        )


class ForecastSerializer(serializers.ModelSerializer):
    """Forecast list serializer."""

    store = serializers.SlugRelatedField(
        slug_field="store",
        queryset=Store.objects.all(),
    )
    sku = serializers.SlugRelatedField(
        slug_field="sku",
        queryset=SKU.objects.all(),
    )

    class Meta:
        """Forecast list serializer meta."""

        model = Forecast
        fields = (
            "store",
            "sku",
            "forecast_date",
            "forecast",
        )