from datetime import datetime

import pytz
from django.test import TestCase

from forecasts.models import SKU, Sale, Store


class SaleModelTestCase(TestCase):
    """Sale model testcase class."""

    def setUp(self):
        """Create sample Store, SKU, and Sale instances for testing."""
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
        self.sale = Sale.objects.create(
            store=self.store,
            sku=self.sku,
            date=timezone.localize(
                datetime.strptime("2023-09-26T12:00:00", "%Y-%m-%dT%H:%M:%S")
            ),
            sales_type=True,
            sales_units=50,
            sales_units_promo=25,
            sales_rub=1000.0,
            sales_rub_promo=500.0,
        )

    def test_str_method(self):
        """Test the __str__ method of sales."""
        expected_str = f"{self.sku} sale in {self.store} at {self.sale.date}"
        self.assertEqual(str(self.sale), expected_str)

    def test_model_fields(self):
        """Test model fields."""
        sale_from_db = Sale.objects.get(pk=self.sale.pk)

        self.assertEqual(sale_from_db.store, self.store)
        self.assertEqual(sale_from_db.sku, self.sku)
        self.assertEqual(sale_from_db.date, self.sale.date)
        self.assertEqual(sale_from_db.sales_type, True)
        self.assertEqual(sale_from_db.sales_units, 50)
        self.assertEqual(sale_from_db.sales_units_promo, 25)
        self.assertEqual(sale_from_db.sales_rub, 1000.0)
        self.assertEqual(sale_from_db.sales_rub_promo, 500.0)

    def test_model_verbose_names(self):
        """Test the verbose names of model fields."""
        self.assertEqual(Sale._meta.get_field("store").verbose_name, "Магазин")
        self.assertEqual(
            Sale._meta.get_field("sku").verbose_name, "Наименование товара"
        )
        self.assertEqual(
            Sale._meta.get_field("date").verbose_name, "Дата продажи"
        )
        self.assertEqual(
            Sale._meta.get_field("sales_type").verbose_name, "Наличие промо"
        )
        self.assertEqual(
            Sale._meta.get_field("sales_units").verbose_name,
            "Число проданных товаров без промо",
        )
        self.assertEqual(
            Sale._meta.get_field("sales_units_promo").verbose_name,
            "Число проданных товаров c промо",
        )
        self.assertEqual(
            Sale._meta.get_field("sales_rub").verbose_name,
            "Сумма продаж без промо в рублях",
        )
        self.assertEqual(
            Sale._meta.get_field("sales_rub_promo").verbose_name,
            "Сумма продаж c промо в рублях",
        )

    def test_model_plural_verbose_name(self):
        """Test the plural verbose name of the model."""
        self.assertEqual(str(Sale._meta.verbose_name_plural), "Продажи")
