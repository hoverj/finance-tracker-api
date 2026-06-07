from django.db import models
from finances.category.models import Category
from django.utils import timezone


class Transaction(models.Model):

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure that only transactions with a category of the correct type can be saved
        if self.category.category_type == Category.INCOME and self.amount < 0:
            raise ValueError("Income transactions must have a positive amount.")
        if self.category.category_type == Category.EXPENSE and self.amount > 0:
            raise ValueError("Expense transactions must have a negative amount.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.date})"
