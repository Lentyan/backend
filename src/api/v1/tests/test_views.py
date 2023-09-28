from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from forecasts.models import SKU


class SKUViewSetTest(TestCase):
    """SKU view set testcase class."""

    def setUp(self):
        """Create sample client and SKU for testing."""
        self.client = APIClient()
        self.url = "/api/v1/categories/"

        skus = []
        for i in range(5):
            skus.append(
                SKU(
                    group=f"Group{i}",
                    category=f"Category{i}",
                    subcategory=f"Subcategory{1}",
                    sku=f"SKU{1}",
                    uom=17,
                )
            )
        SKU.objects.bulk_create(skus)

    def test_list_skus(self):
        """Test view return valid list response."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_retrieve_sku(self):
        """Test view return valid retrieve response."""
        sku = SKU.objects.first()
        response = self.client.get(f"{self.url}{sku.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group"], sku.group)
