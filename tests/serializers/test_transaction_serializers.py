from rest_framework.test import APIRequestFactory
from finances.transaction.serializers import TransactionSerializer
from finances.category.models import Category
from django.contrib.auth.models import User
import pytest


class TestTransactionSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        factory = APIRequestFactory()
        self.user_category_expense = Category.objects.create(
            name="Expense Category", category_type=Category.EXPENSE, user=self.user
        )
        self.user_category_income = Category.objects.create(
            name="Income Category", category_type=Category.INCOME, user=self.user
        )
        self.request = factory.get("/")
        self.request.user = self.user

    def test_transaction_serializer_valid(self):
        data = {
            "category": self.user_category_expense.id,
            "amount": -50.00,
            "date": "2024-06-01",
            "description": "Grocery shopping",
        }
        serializer = TransactionSerializer(data=data, context={"request": self.request})
        assert serializer.is_valid(), serializer.errors

    def test_transaction_serializer_negative_amount_for_income_category(self):
        data = {
            "category": self.user_category_income.id,
            "amount": -100.00,
            "date": "2024-06-01",
            "description": "Salary",
        }
        serializer = TransactionSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_transaction_serializer_positive_amount_for_expense_category(self):
        data = {
            "category": self.user_category_expense.id,
            "amount": 100.00,
            "date": "2024-06-01",
            "description": "Grocery shopping",
        }
        serializer = TransactionSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_transaction_serializer_category_not_belonging_to_user(self):
        other_user = User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="otherpass123"
        )
        other_user_category = Category.objects.create(
            name="Other User Category", category_type=Category.EXPENSE, user=other_user
        )
        data = {
            "category": other_user_category.id,
            "amount": -50.00,
            "date": "2024-06-01",
            "description": "Grocery shopping",
        }
        serializer = TransactionSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_partial_update_transaction_serializer(self):
        # Create a transaction instance to update
        transaction = TransactionSerializer(
            data={
                "category": self.user_category_expense.id,
                "amount": -50.00,
                "date": "2024-06-01",
                "description": "Grocery shopping",
            },
            context={"request": self.request},
        )
        assert transaction.is_valid(), transaction.errors
        transaction_instance = transaction.save()

        # Update the transaction's amount and description
        update_data = {
            "amount": -75.00,
            "description": "Updated grocery shopping",
        }
        serializer = TransactionSerializer(
            instance=transaction_instance,
            data=update_data,
            partial=True,
            context={"request": self.request},
        )
        assert serializer.is_valid(), serializer.errors
        updated_transaction = serializer.save()
        assert updated_transaction.amount == -75.00
        assert updated_transaction.description == "Updated grocery shopping"
