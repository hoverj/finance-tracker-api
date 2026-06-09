from rest_framework.routers import DefaultRouter
from finances.category.views import CategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
