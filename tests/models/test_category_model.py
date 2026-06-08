import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from finances.category.models import Category


@pytest.mark.django_db
class TestCategoryModel:

    def setup_method(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_category(self):
        category = Category.objects.create(
            user=self.user,
            name="Groceries",
            category_type=Category.EXPENSE,
            color="#FF0000",
        )
        assert category.name == "Groceries"
        assert category.category_type == Category.EXPENSE
        assert category.color == "#FF0000"
        assert category.user == self.user
        assert Category.objects.count() == 1

    @pytest.mark.parametrize(
        "missing_field",
        [
            "name",
            "category_type",
            "user",
        ],
    )
    def test_missing_required_field(self, missing_field):
        category_data = {
            "user": self.user,
            "name": "Utilities",
            "category_type": Category.EXPENSE,
            "color": "#00FF00",
        }
        category_data.pop(missing_field)

        with pytest.raises(ValidationError):
            Category.objects.create(**category_data)

    def test_delete_category_without_deleting_user(self):
        category = Category.objects.create(
            user=self.user,
            name="Entertainment",
            category_type=Category.EXPENSE,
            color="#0000FF",
        )
        category.delete()
        assert Category.objects.count() == 0
        assert User.objects.filter(id=self.user.id).exists()

    def test_color_field_default(self):
        category = Category.objects.create(
            user=self.user,
            name="Health",
            category_type=Category.EXPENSE,
        )
        assert category.color is not None
        assert category.color == "#000000"

    def test__str__method(self):
        category = Category.objects.create(
            user=self.user,
            name="Salary",
            category_type=Category.INCOME,
            color="#00FF00",
        )
        assert (
            str(category) == f"{category.name} ({category.get_category_type_display()})"
        )

    def test_user_delete_category_cascade(self):
        some_other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )

        category = Category.objects.create(
            user=self.user,
            name="Travel",
            category_type=Category.EXPENSE,
            color="#FF00FF",
        )
        category_other_user = Category.objects.create(
            user=some_other_user,
            name="Investment",
            category_type=Category.INCOME,
            color="#00FFFF",
        )
        assert Category.objects.count() == 2
        self.user.delete()
        assert Category.objects.count() == 1

    def test_invalid_category_type(self):
        with pytest.raises(ValidationError):
            Category.objects.create(
                user=self.user,
                name="Invalid",
                category_type="invalid_type",
                color="#123456",
            )

    def test_unique_category_name_per_user(self):
        SAME_NAME = "UniqueName"
        Category.objects.create(
            user=self.user,
            name=SAME_NAME,
            category_type=Category.EXPENSE,
            color="#654321",
        )
        with pytest.raises(ValidationError):
            Category.objects.create(
                user=self.user,
                name=SAME_NAME,
                category_type=Category.INCOME,
                color="#654321",
            )
