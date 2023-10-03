from django.db import IntegrityError
from django.test import TestCase

from forecasts.models import SKU


class SKUModelTestCase(TestCase):
    """SKU model testcase class."""

    def setUp(self):
        """Create sample SKU instances for testing."""
        self.sku = SKU.objects.create(
            group="Group1",
            category="Category1",
            subcategory="Subcategory1",
            sku="SKU123",
            uom=10,
        )

    def test_str_method(self):
        """Test the __str__ method of SKU."""
        self.assertEqual(str(self.sku), "Sku123")

    def test_unique_constraint(self):
        """Test creating a duplicate SKU raise an IntegrityError."""
        with self.assertRaises(Exception) as context:
            SKU.objects.create(
                group="Group1",
                category="Category1",
                subcategory="Subcategory1",
                sku="SKU123",
                uom=10,
            )

        self.assertEqual(type(context.exception), IntegrityError)

    def test_model_fields(self):
        """Test model fields."""
        sku_from_db = SKU.objects.get(pk=self.sku.pk)

        self.assertEqual(sku_from_db.group, "Group1")
        self.assertEqual(sku_from_db.category, "Category1")
        self.assertEqual(sku_from_db.subcategory, "Subcategory1")
        self.assertEqual(sku_from_db.sku, "SKU123")
        self.assertEqual(sku_from_db.uom, 10)

    def test_model_verbose_names(self):
        """Test the verbose names of model fields."""
        self.assertEqual(SKU._meta.get_field("group").verbose_name, "Группа")
        self.assertEqual(
            SKU._meta.get_field("category").verbose_name, "Категория"
        )
        self.assertEqual(
            SKU._meta.get_field("subcategory").verbose_name, "Подкатегория"
        )
        self.assertEqual(
            SKU._meta.get_field("sku").verbose_name, "Наименование товара"
        )
        self.assertEqual(
            SKU._meta.get_field("uom").verbose_name, "Единицы измерения"
        )

    def test_model_plural_verbose_name(self):
        """Test the plural verbose name of the model."""
        self.assertEqual(str(SKU._meta.verbose_name_plural), "Товары")
