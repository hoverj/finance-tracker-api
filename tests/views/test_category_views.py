from rest_framework.test import APIClient
from rest_framework import status
import pytest
from django.contrib.auth.models import User
from finances.category.models import Category


class TestCategoryViews:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_categories(self):
        some_object = Category.objects.create(
            user=self.user,
            name="Test Category",
            category_type="income",
            color="#00FF00",
        )

        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass123"
        )
        Category.objects.create(
            user=another_user,
            name="Another Category",
            category_type="expense",
            color="#FF0000",
        )

        response = self.client.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["name"] == some_object.name

    def test_successful_create_category(self):
        data = {"name": "Testing", "category_type": "expense", "color": "#FF5733"}
        response = self.client.post("/api/categories/", data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="Testing", user=self.user).exists()

    def test_failed_create_category_with_invalid_data(self):
        data = {"name": "", "category_type": "invalid_type", "color": "not_a_color"}
        response = self.client.post("/api/categories/", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Category.objects.filter(name="", user=self.user).exists()

    def test_user_ignored_on_create_category(self):
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass123"
        )
        data = {
            "name": "Testing",
            "category_type": "income",
            "color": "#00FF00",
            "user": another_user.id,
        }
        response = self.client.post("/api/categories/", data=data)
        assert response.status_code == status.HTTP_201_CREATED
        category = Category.objects.get(name="Testing")
        assert category.user == self.user

    def test_unauthenticated_user_cannot_create_category(self):
        self.client.force_authenticate(user=None)
        data = {"name": "Testing", "category_type": "expense", "color": "#FF5733"}
        response = self.client.post("/api/categories/", data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
