from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from forecasts.models import SKU
from users.models import User


class SKUViewSetTest(TestCase):
    """SKU view set testcase class."""

    def setUp(self):
        """Create sample client and SKU for testing."""
        self.url = "/api/v1/categories/"
        self.user = User.objects.create_user(
            email="test@mail.com",
            first_name="FirstName",
            last_name="LastName",
            password="password",
        )
        self.anonim_client = APIClient()
        self.auth_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.auth_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

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
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_retrieve_sku(self):
        """Test view return valid retrieve response."""
        sku = SKU.objects.first()
        response = self.auth_client.get(f"{self.url}{sku.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group"], sku.group)
