from rest_framework.test import APIClient
from rest_framework import status
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from finances.category.models import Category
from finances.transaction.models import Transaction


class TestTransactionViews:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.category_income = Category.objects.create(
            user=self.user,
            name="Income Category",
            category_type="income",
            color="#00FF00",
        )
        self.category_expense = Category.objects.create(
            user=self.user,
            name="Expense Category",
            category_type="expense",
            color="#FF0000",
        )

    def test_authenticated_user_can_create_transaction(self):
        data = {
            "amount": 100.00,
            "date": "2024-01-01",
            "description": "Test Transaction",
            "category": self.category_income.id,
        }
        response = self.client.post(reverse("transaction-list"), data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Transaction.objects.filter(
            description="Test Transaction", category=self.category_income
        ).exists()

    def test_transaction_creation_fails_with_invalid_data(self):
        data = {
            "amount": -50.00,  # Invalid amount
            "date": "invalid-date",  # Invalid date
            "description": "",
            "category": self.category_expense.id,
        }
        response = self.client.post(reverse("transaction-list"), data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Transaction.objects.filter(
            description="", category=self.category_expense
        ).exists()

    def test_user_cannot_create_transaction_for_other_users_category(self):
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass123"
        )
        another_category = Category.objects.create(
            user=another_user,
            name="Another User's Category",
            category_type="expense",
            color="#0000FF",
        )
        data = {
            "amount": -50.00,
            "date": "2024-01-01",
            "description": "Another Users Transaction Category",
            "category": another_category.id,
        }
        response = self.client.post(reverse("transaction-list"), data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Transaction.objects.filter(
            description="Another Users Transaction Category", category=another_category
        ).exists()

    def test_unauthenticated_user_cannot_create_transaction(self):
        self.client.force_authenticate(user=None)
        data = {
            "amount": 100.00,
            "date": "2024-01-01",
            "description": "Test Transaction",
            "category": self.category_income.id,
        }
        response = self.client.post(reverse("transaction-list"), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_retrieve_transaction(self):
        transaction = Transaction.objects.create(
            amount=100.00,
            date="2024-01-01",
            description="Test Transaction",
            category=self.category_income,
        )
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("transaction-detail", args=[transaction.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authenticated_user_cannot_retrieve_other_users_transaction(self):
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass123"
        )
        another_category = Category.objects.create(
            user=another_user,
            name="Another User's Category",
            category_type="expense",
            color="#0000FF",
        )
        transaction = Transaction.objects.create(
            amount=-50.00,
            date="2024-01-01",
            description="Another Users Transaction",
            category=another_category,
        )
        response = self.client.get(reverse("transaction-detail", args=[transaction.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_authenticated_user_can_update_own_transaction(self):
        transaction = Transaction.objects.create(
            amount=100.00,
            date="2024-01-01",
            description="Test Transaction",
            category=self.category_income,
        )
        data = {
            "amount": 150.00,
            "date": "2024-01-02",
            "description": "Updated Transaction",
            "category": self.category_income.id,
        }
        response = self.client.put(
            reverse("transaction-detail", args=[transaction.id]), data=data
        )
        assert response.status_code == status.HTTP_200_OK
        transaction.refresh_from_db()
        assert transaction.amount == 150.00
        assert str(transaction.date) == "2024-01-02"

    def test_authenticated_user_cannot_update_others_transaction(self):
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass123"
        )
        another_category = Category.objects.create(
            user=another_user,
            name="Another User's Category",
            category_type="expense",
            color="#0000FF",
        )
        transaction = Transaction.objects.create(
            amount=-50.00,
            date="2024-01-01",
            description="Another Users Transaction",
            category=another_category,
        )
        data = {
            "amount": -100.00,
            "date": "2024-01-02",
            "description": "Updated Transaction",
        }
        response = self.client.put(
            reverse("transaction-detail", args=[transaction.id]), data=data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_authenticated_user_can_delete_own_transaction(self):
        transaction = Transaction.objects.create(
            amount=100.00,
            date="2024-01-01",
            description="Test Transaction",
            category=self.category_income,
        )
        assert Transaction.objects.filter(id=transaction.id).exists()
        response = self.client.delete(
            reverse("transaction-detail", args=[transaction.id])
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Transaction.objects.filter(id=transaction.id).exists()

    def test_authenticated_user_cannot_delete_others_transaction(self):
        some_other_user = User.objects.create_user(
            username="someotheruser", password="someotherpass123"
        )
        category = Category.objects.create(
            user=some_other_user,
            name="Some Other User's Category",
            category_type="expense",
            color="#123456",
        )
        transaction = Transaction.objects.create(
            amount=-100.00,
            date="2024-01-01",
            description="Test Transaction",
            category=category,
        )

        assert Transaction.objects.filter(id=transaction.id).exists()
        response = self.client.delete(
            reverse("transaction-detail", args=[transaction.id])
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Transaction.objects.filter(id=transaction.id).exists()
