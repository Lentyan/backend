import django_filters

from forecasts.models import Forecast, Sale


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

    class Meta:
        """Meta of filter class for Sale model."""

        model = Sale
        fields = {
            "store": ["exact"],
            "sku": ["exact"],
            "date": ["exact", "gte", "lte"],
        }
