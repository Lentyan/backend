import csv
import os

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from forecasts.models import SKU
from users.models import User


class SKUViewSetTest(TestCase):
    """SKU view set testcase class."""

    def create_csv_file(self, data):
        """Create csv file from data."""
        file_path = "./test_data.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)
        return file_path

    def setUp(self):
        """Create sample client and SKU for testing."""
        self.csv_data = [
            [
                "pr_sku_id",
                "pr_group_id",
                "pr_cat_id",
                "pr_subcat_id",
                "pr_uom_id",
            ],
            ["CSVGroup1", "CSVCategory1", "CSVSubcategory1", "CSVSKU", 17],
            ["CSVGroup2", "CSVCategory2", "CSVSubcategory2", "CSVSKU", 1],
        ]
        self.csv_file_path = self.create_csv_file(self.csv_data)

        self.url = "/api/v1/skus/"
        self.user = User.objects.create_user(
            email="test@mail.com",
            first_name="FirstName",
            last_name="LastName",
            password="password",
        )
        self.auth_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.auth_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        skus = [
            SKU(
                group=f"Group{i}",
                category=f"Category{i}",
                subcategory=f"Subcategory{1}",
                sku=f"SKU{1}",
                uom=17,
            )
            for i in range(5)
        ]
        SKU.objects.bulk_create(skus)

    def tearDown(self):
        """Tear down test class."""
        if os.path.exists(self.csv_file_path):
            os.remove(self.csv_file_path)

    def test_create_skus(self):
        """Test create skus from json."""
        objects_num = 3
        data = {
            "data": [
                {
                    "group": f"NewGroup{i}",
                    "category": f"NewCategory{i}",
                    "subcategory": f"Subcategory{1}",
                    "sku": f"NewSKU{1}",
                    "uom": 17,
                }
                for i in range(objects_num)
            ]
        }
        count = SKU.objects.count()
        response = self.auth_client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count + objects_num, SKU.objects.count())

    def test_list_skus(self):
        """Test view return valid list response."""
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_create_from_csv(self):
        """Test create skus from csv file."""
        count = SKU.objects.count()
        with open(self.csv_file_path, "r") as file:
            csv_data = {"csv_file": file}
            response = self.client.post(
                self.url + "create_from_csv/", csv_data, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_sku_count = len(self.csv_data) - 1 + count
        self.assertEqual(SKU.objects.count(), expected_sku_count)

    def test_retrieve_sku(self):
        """Test view return valid retrieve response."""
        sku = SKU.objects.first()
        response = self.auth_client.get(f"{self.url}{sku.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group"], sku.group)
