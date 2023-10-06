from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from forecasts.models import SKU, Forecast, Sale, Store
from users.models import User


class SKUSerializer(serializers.ModelSerializer):
    """SKU model serializer."""

    class Meta:
        """SKU model serializer meta."""

        model = SKU
        fields = (
            "id",
            "sku",
            "group",
            "category",
            "subcategory",
            "uom",
        )


class GroupSerializer(serializers.Serializer):
    """SKU groups list serializer."""

    groups = serializers.ListSerializer(child=serializers.CharField())


class CategorySerializer(serializers.Serializer):
    """SKU categories list serializer."""

    categories = serializers.ListSerializer(child=serializers.CharField())


class SubcategorySerializer(serializers.Serializer):
    """SKU subcategories list serializer."""

    subcategories = serializers.ListSerializer(child=serializers.CharField())


class StoreSerializer(serializers.ModelSerializer):
    """Store model serializer."""

    class Meta:
        """Store model serializer meta."""

        model = Store
        fields = (
            "id",
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
    """Forecast model serializer."""

    store = serializers.SlugRelatedField(
        slug_field="store",
        queryset=Store.objects.all(),
    )
    sku = serializers.SlugRelatedField(
        slug_field="sku",
        queryset=SKU.objects.all(),
    )

    class Meta:
        """Forecast model serializer meta."""

        model = Forecast
        fields = (
            "store",
            "sku",
            "forecast_date",
            "forecast",
        )


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """User model serializer meta."""

        model = User
        fields = ("email", "first_name", "last_name")


class CreateForecastReportSerializer(serializers.Serializer):
    """Create forecast report serializer."""

    store_ids = serializers.ListField(child=serializers.IntegerField())
    groups = serializers.ListField(child=serializers.CharField())
    categories = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    subcategories = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    sku_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate_store_ids(self, store_ids):
        """Validate store_ids are all positive."""
        if not all(map(lambda store_id: store_id > 0, store_ids)):
            raise ValidationError(
                "store_ids must contain positive values.",
            )
        return store_ids

    def validate_from_date(self, from_date):
        """Validate from_date and to_date are present."""
        to_date = self.initial_data.get("to_date")
        if from_date and not to_date:
            raise serializers.ValidationError(
                "to_date is required when from_date is specified."
            )
        return from_date

    def validate_to_date(self, to_date):
        """Validate to_date is later than or equal to from_date."""
        from_date = self.initial_data.get("from_date")
        if from_date and not to_date:
            raise serializers.ValidationError(
                "from_date is required when to_date is specified."
            )
        if from_date and to_date < date.fromisoformat(str(from_date)):
            raise serializers.ValidationError(
                "to_date cant be earlier than from_date."
            )
        return to_date


class ForecastUploadSerializer(serializers.Serializer):
    """Load forecast from csv serializer."""

    csv_file = serializers.FileField()

    def validate_csv_file(self, csv_file):
        """Validate csv file format."""
        if not csv_file.name.endswith(".csv"):
            raise serializers.ValidationError(
                "File must have a CSV extension."
            )
        return csv_file
