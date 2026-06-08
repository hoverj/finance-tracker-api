from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    CATEGORY_TYPES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default="#000000")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_category_type_display(self):
        return dict(self.CATEGORY_TYPES).get(self.category_type, "Unknown")

    def save(self, *args, **kwargs):
        # Ensure that the empty string fields are not saved as empty strings but rather as null values
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ("name", "user")

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
