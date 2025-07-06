from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CategorizationRuleViewSet

app_name = "categories"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"rules", CategorizationRuleViewSet, basename="rules")

urlpatterns = [
    path("", include(router.urls)),
]