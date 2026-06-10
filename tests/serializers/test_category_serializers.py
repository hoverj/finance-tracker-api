from rest_framework.test import APIRequestFactory
from finances.category.serializers import CategorySerializer
from django.contrib.auth.models import User
import pytest


class TestCategorySerializer:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        factory = APIRequestFactory()

        self.request = factory.get("/")
        self.request.user = self.user

    def test_category_serializer_valid(self):
        data = {
            "name": "Groceries",
            "category_type": "expense",
            "color": "#FF0000",
        }
        serializer = CategorySerializer(data=data, context={"request": self.request})
        assert serializer.is_valid(), serializer.errors

    def test_category_serializer_invalid(self):
        data = {
            "name": "",
            "category_type": "invalid_type",
            "color": "not_a_color",
        }
        serializer = CategorySerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        assert "category_type" in serializer.errors
        assert "color" in serializer.errors

    def test_category_serializer_create(self):
        data = {
            "name": "Utilities",
            "category_type": "expense",
            "color": "#0000FF",
        }
        serializer = CategorySerializer(data=data, context={"request": self.request})
        assert serializer.is_valid(), serializer.errors
        category = serializer.save(user=self.request.user)
        assert category.name == data["name"]
        assert category.category_type == data["category_type"]
        assert category.color == data["color"]
        assert category.user == self.request.user

    def test_category_serializer_partial_update(self):
        category = CategorySerializer(
            data={
                "name": "Entertainment",
                "category_type": "expense",
                "color": "#00FF00",
            },
            context={"request": self.request},
        )
        assert category.is_valid(), category.errors
        category_instance = category.save(user=self.request.user)

        update_data = {
            "name": "Entertainment Updated",
        }
        serializer = CategorySerializer(
            instance=category_instance,
            data=update_data,
            partial=True,
            context={"request": self.request},
        )
        assert serializer.is_valid(), serializer.errors
        updated_category = serializer.save()
        assert updated_category.name == update_data["name"]

    def test_user_field_is_read_only(self):
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        data = {
            "name": "Groceries",
            "category_type": "expense",
            "color": "#FF0000",
            "user": other_user.id,
        }
        serializer = CategorySerializer(data=data, context={"request": self.request})
        assert serializer.is_valid(), serializer.errors
        category = serializer.save(user=self.request.user)
        assert category.user == self.request.user
        assert category.user != other_user
