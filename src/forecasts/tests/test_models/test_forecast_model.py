from datetime import datetime

import pytz
from django.test import TestCase

from forecasts.models import SKU, Forecast, Store


class ForecastModelTestCase(TestCase):
    """Forecast model testcase class."""

    def setUp(self):
        """Create sample Store, SKU, and Forecast instances for testing."""
        timezone = pytz.timezone("UTC")

        self.store = Store.objects.create(
            store="Store1",
            city="City1",
            division="Division1",
            type_format=1,
            loc=2,
            size=3,
            is_active=True,
        )
        self.sku = SKU.objects.create(
            group="Group1",
            category="Category1",
            subcategory="Subcategory1",
            sku="SKU123",
            uom=10,
        )
        self.forecast = Forecast.objects.create(
            store=self.store,
            sku=self.sku,
            forecast_date=timezone.localize(
                datetime.strptime("2023-09-26T12:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            forecast={"value": 100},
        )

    def test_str_method(self):
        """Test the __str__ method of Forecast."""
        expected_str = (
            f"{self.sku} forecast for {self.store} "
            f"at {self.forecast.forecast_date}"
        )
        self.assertEqual(str(self.forecast), expected_str)

    def test_model_fields(self):
        """Test model fields."""
        forecast_from_db = Forecast.objects.get(pk=self.forecast.pk)

        self.assertEqual(forecast_from_db.store, self.store)
        self.assertEqual(forecast_from_db.sku, self.sku)
        self.assertEqual(
            forecast_from_db.forecast_date,
            self.forecast.forecast_date,
        )
        self.assertEqual(forecast_from_db.forecast, {"value": 100})

    def test_model_verbose_names(self):
        """Test the verbose names of model fields."""
        self.assertEqual(
            Forecast._meta.get_field("store").verbose_name, "Магазин"
        )
        self.assertEqual(Forecast._meta.get_field("sku").verbose_name, "Товар")
        self.assertEqual(
            Forecast._meta.get_field("forecast_date").verbose_name,
            "Дата прогноза",
        )

    def test_model_plural_verbose_name(self):
        """Test the plural verbose name of the model."""
        self.assertEqual(str(Forecast._meta.verbose_name_plural), "Прогнозы")
