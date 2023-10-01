import django_filters
from django.forms import CharField, IntegerField, MultipleChoiceField
from django_filters import Filter

from forecasts.models import SKU, Forecast, Sale


class MultipleValueField(MultipleChoiceField):
    """A custom form field that represents a list of multiple values."""

    def __init__(self, *args, field_class, **kwargs):
        """Initialize the MultipleValueField."""
        self.inner_field = field_class()
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        """Validate a single value using the inner field's validation."""
        return self.inner_field.validate(value)

    def clean(self, values):
        """Clean a list of values using the inner field's cleaning."""
        return values and [self.inner_field.clean(value) for value in values]


class MultipleValueFilter(Filter):
    """A custom filter for filtering by a list of multiple values."""

    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        """Initialize the MultipleValueFilter."""
        kwargs.setdefault("lookup_expr", "in")
        super().__init__(*args, field_class=field_class, **kwargs)


class ForecastFilter(django_filters.FilterSet):
    """
    Filter class for Forecast model.

    This filter class defines filters for the Forecast model,
    allowing to filter forecasts based on store, SKU, and forecast date.
    """

    class Meta:
        """Meta of filter class for Forecast model."""

        model = Forecast
        fields = {
            "store": ["exact"],
            "sku": ["exact"],
            "forecast_date": ["exact", "gte", "lte"],
        }


class SaleFilter(django_filters.FilterSet):
    """
    Filter class for Sale model.

    This filter class defines filters for the Sale model,
    allowing to filter sales based on store, SKU, and date.
    """

    store = MultipleValueFilter(field_class=IntegerField)
    sku = MultipleValueFilter(field_class=IntegerField)
    date = django_filters.DateTimeFilter()
    date__gte = django_filters.NumberFilter(
        field_name="date", lookup_expr="gte"
    )
    date__lte = django_filters.NumberFilter(
        field_name="date", lookup_expr="lte"
    )

    class Meta:
        """Meta of filter class for Sale model."""

        model = Sale
        fields = ["store", "sku", "date"]


class SKUFilter(django_filters.FilterSet):
    """
    Filter class for Forecast model.

    This filter class defines filters for the Forecast model,
    allowing to filter forecasts based on store, SKU, and forecast date.
    """

    group = MultipleValueFilter(field_class=CharField)
    category = MultipleValueFilter(field_class=CharField)
    subcategory = MultipleValueFilter(field_class=CharField)

    class Meta:
        """Meta of filter class for Forecast model."""

        model = SKU
        fields = [
            "group",
            "category",
            "subcategory",
        ]


class CategoryFilter(django_filters.FilterSet):
    """
    Filter class for SKU categories.

    This filter class defines filters for the SKU categories,
    allowing to filter categories based on groups.
    """

    group = MultipleValueFilter(field_class=CharField)

    class Meta:
        """Meta of filter class for SKU categories."""

        model = SKU
        fields = [
            "group",
        ]


class SubcategoryFiler(CategoryFilter):
    """
    Filter class for SKU subcategories.

    This filter class defines filters for the SKU subcategories,
    allowing to filter subcategories based on groups and categories.
    """

    category = MultipleValueFilter(field_class=CharField)

    class Meta(CategoryFilter.Meta):
        """Meta of filter class for SKU subcategories."""

        fields = CategoryFilter.Meta.fields + ["category"]
