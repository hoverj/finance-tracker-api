from rest_framework import serializers
from finances.category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "category_type", "color", "name", "user"]
