from collections import OrderedDict
from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from api.v1 import filters
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


class ForecastDataSerializer(serializers.Serializer):
    """Forecast data serializer."""

    target = serializers.IntegerField()
    date = serializers.DateField()

    def to_representation(self, instance):
        """Convert instance to dict representation."""
        return {str(entry["date"]): entry["target"] for entry in instance}


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

    forecast_date = serializers.SerializerMethodField(read_only=True)

    forecast = serializers.SerializerMethodField(read_only=True)

    date = serializers.DateField(write_only=True)

    target = serializers.IntegerField(write_only=True)

    class Meta:
        """Forecast model serializer meta."""

        model = Forecast
        fields = (
            "store",
            "sku",
            "forecast_date",
            "forecast",
            "date",
            "target",
        )

    def get_forecast(self, forecast):
        """Serialize method to get forecast as JSON."""
        queryset = Forecast.objects.filter(
            sku=forecast.get("sku"), store=forecast.get("store")
        )
        forecasts = (
            filters.ForecastFilter(
                self.context["request"].GET,
                queryset,
            )
            .qs.values("date", "target")
            .order_by("date")
        )
        return ForecastDataSerializer(forecasts).data

    def get_forecast_date(self, forecast_date):
        """Return required forecast date."""
        return self.context["request"].query_params.get("forecast_date")

    def to_representation(self, instance):
        """Return data as ordered dict."""
        ret = OrderedDict(instance)
        fields = self._readable_fields

        for field in fields:
            if field.field_name in ret:
                continue
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            check_for_none = (
                attribute.pk
                if isinstance(attribute, PKOnlyObject)
                else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret


class ForecastPostSerializer(serializers.Serializer):
    """Bulk load forecast serializer."""

    data = serializers.ListSerializer(child=ForecastSerializer())


class SKUPostSerializer(serializers.Serializer):
    """Bulk load SKU serializer."""

    data = serializers.ListSerializer(child=SKUSerializer())


class StorePostSerializer(serializers.Serializer):
    """Bulk load store serializer."""

    data = serializers.ListSerializer(child=StoreSerializer())


class SalePostSerializer(serializers.Serializer):
    """Bulk load sale serializer."""

    data = serializers.ListSerializer(child=SaleSerializer())


class CSVFileSerializer(serializers.Serializer):
    """Load forecast from csv serializer."""

    csv_file = serializers.FileField()

    def validate_csv_file(self, csv_file):
        """Validate csv file format."""
        if not csv_file.name.endswith(".csv"):
            raise serializers.ValidationError(
                "File must have a CSV extension."
            )
        return csv_file


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
    forecast_date = serializers.DateField()
    categories = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    subcategories = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    sku_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    from_date = serializers.DateField()
    to_date = serializers.DateField()

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


class CreateStatisticsReportSerializer(serializers.Serializer):
    """Create statistics report serializer."""

    store_ids = serializers.ListField(child=serializers.IntegerField())
    forecast_date = serializers.DateField()
    sku_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
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
