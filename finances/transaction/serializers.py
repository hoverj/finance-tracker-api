from rest_framework import serializers
from finances.category.models import Category
from finances.transaction.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    def validate(self, data):
        request = self.context.get("request")
        user = request.user if request else None

        category = self.instance.category if self.instance else data.get("category")
        if not category:
            raise serializers.ValidationError("Category is required.")
        if category.user != user:
            raise serializers.ValidationError("Category does not belong to the user.")

        amount = data.get("amount", self.instance.amount if self.instance else None)
        if amount is None:
            raise serializers.ValidationError("Amount is required.")

        if category.category_type == Category.INCOME and amount < 0:
            raise serializers.ValidationError(
                "Income transactions must have a positive amount."
            )
        if category.category_type == Category.EXPENSE and amount > 0:
            raise serializers.ValidationError(
                "Expense transactions must have a negative amount."
            )
        return data

    class Meta:
        model = Transaction
        fields = ["id", "category", "amount", "date", "description", "updated_at"]
