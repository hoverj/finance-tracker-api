import pytest
from django.utils import timezone
import time
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from finances.category.models import Category
from finances.transaction.models import Transaction


@pytest.mark.django_db
class TestTransactionModel:

    def setup_method(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category_income = Category.objects.create(
            user=self.user,
            name="Salary",
            category_type=Category.INCOME,
            color="#00FF00",
        )
        self.category_expense = Category.objects.create(
            user=self.user,
            name="Dinner",
            category_type=Category.EXPENSE,
            color="#00FF00",
        )

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            category=self.category_income,
            amount=1000.00,
            description="Monthly salary",
            date=timezone.localdate(),
        )
        assert transaction.category == self.category_income
        assert transaction.amount == 1000.00
        assert transaction.description == "Monthly salary"
        assert transaction.date == timezone.localdate()
        assert Transaction.objects.count() == 1

    @pytest.mark.parametrize(
        "missing_field",
        [
            "category",
            "amount",
        ],
    )
    def test_missing_required_field(self, missing_field):
        transaction_data = {
            "category": self.category_income,
            "amount": 1000.00,
            "description": "Monthly salary",
            "date": timezone.localdate(),
        }
        transaction_data.pop(missing_field)

        with pytest.raises(ValidationError):
            Transaction.objects.create(**transaction_data)

    @pytest.mark.parametrize(
        "amount, category_type",
        [
            (-1000, "income"),
            (1000, "expense"),
        ],
    )
    def test_transaction_amount_category_mismatch(self, amount, category_type):
        category = (
            self.category_income if category_type == "income" else self.category_expense
        )
        with pytest.raises(ValueError):
            Transaction.objects.create(
                category=category,
                amount=amount,
                description="Invalid salary",
                date=timezone.localdate(),
            )

    @pytest.mark.parametrize(
        "amount, category_type",
        [
            (1000, "income"),
            (-1000, "expense"),
        ],
    )
    def test_transaction_amount_category_aligned(self, amount, category_type):
        category = (
            self.category_income if category_type == "income" else self.category_expense
        )

        transaction = Transaction.objects.create(
            category=category,
            amount=amount,
            description="Invalid salary",
            date=timezone.localdate(),
        )
        assert transaction.amount == amount
        assert transaction.category == category

    def test_delete_transaction_without_deleting_category(self):
        transaction = Transaction.objects.create(
            category=self.category_income,
            amount=1000.00,
            description="Monthly salary",
            date=timezone.localdate(),
        )
        transaction.delete()
        assert Transaction.objects.count() == 0
        assert Category.objects.filter(id=self.category_income.id).exists()

    def test_delete_category_deletes_transaction(self):
        transaction = Transaction.objects.create(
            category=self.category_income,
            amount=1000.00,
            description="Monthly salary",
            date=timezone.localdate(),
        )
        self.category_income.delete()
        assert Transaction.objects.count() == 0

    def test__str__method(self):
        transaction = Transaction.objects.create(
            category=self.category_expense,
            amount=-50.00,
            description="Dinner with friends",
            date=timezone.localdate(),
        )
        expected_str = (
            f"{self.category_expense.name} - {transaction.amount} ({transaction.date})"
        )
        assert str(transaction) == expected_str

    def test_date_is_set_to_current_date_by_default(self):
        transaction = Transaction.objects.create(
            category=self.category_income,
            amount=1000.00,
            description="Monthly salary",
        )
        assert transaction.date == timezone.localdate()

    def test_updated_at_is_updated_on_save(self):
        transaction = Transaction.objects.create(
            category=self.category_income,
            amount=1000.00,
            description="Monthly salary",
        )
        original_updated_at = transaction.updated_at
        time.sleep(0.01)  # 10ms delay to ensure timestamp difference
        transaction.description = "Updated description"
        transaction.save()
        transaction.refresh_from_db()
        assert transaction.updated_at > original_updated_at
