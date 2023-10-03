from django.db import IntegrityError
from django.test import TestCase

from forecasts.models import Store


class StoreModelTestCase(TestCase):
    """Store model testcase class."""

    def setUp(self):
        """Create sample Store instances for testing."""
        self.store = Store.objects.create(
            store="Store1",
            city="City1",
            division="Division1",
            type_format=1,
            loc=2,
            size=3,
            is_active=True,
        )

    def test_str_method(self):
        """Test the __str__ method of Store."""
        self.assertEqual(str(self.store), "Store1")

    def test_unique_constraint(self):
        """Test creating a duplicate Store raise an IntegrityError."""
        with self.assertRaises(Exception) as context:
            Store.objects.create(
                store="Store1",
                city="City1",
                division="Division1",
                type_format=1,
                loc=2,
                size=3,
                is_active=True,
            )

        self.assertEqual(type(context.exception), IntegrityError)

    def test_model_fields(self):
        """Test model fields."""
        store_from_db = Store.objects.get(pk=self.store.pk)

        self.assertEqual(store_from_db.store, "Store1")
        self.assertEqual(store_from_db.city, "City1")
        self.assertEqual(store_from_db.division, "Division1")
        self.assertEqual(store_from_db.type_format, 1)
        self.assertEqual(store_from_db.loc, 2)
        self.assertEqual(store_from_db.size, 3)
        self.assertEqual(store_from_db.is_active, True)

    def test_model_verbose_names(self):
        """Test the verbose names of model fields."""
        self.assertEqual(
            Store._meta.get_field("store").verbose_name, "Название магазина"
        )
        self.assertEqual(
            Store._meta.get_field("city").verbose_name, "Населенный пункт"
        )
        self.assertEqual(
            Store._meta.get_field("division").verbose_name, "Дивизион"
        )
        self.assertEqual(
            Store._meta.get_field("type_format").verbose_name,
            "Формат магазина",
        )
        self.assertEqual(
            Store._meta.get_field("loc").verbose_name,
            "Локация/окружение магазина",
        )
        self.assertEqual(
            Store._meta.get_field("size").verbose_name, "Размер магазина"
        )
        self.assertEqual(
            Store._meta.get_field("is_active").verbose_name, "Активен"
        )

    def test_model_plural_verbose_name(self):
        """Test the plural verbose name of the model."""
        self.assertEqual(str(Store._meta.verbose_name_plural), "Магазины")
