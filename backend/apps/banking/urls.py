from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BankProviderViewSet,
    BankAccountViewSet,
    TransactionViewSet,
    BankingSyncViewSet,
)

app_name = "banking"

router = DefaultRouter()
router.register(r"providers", BankProviderViewSet, basename="bank-providers")
router.register(r"accounts", BankAccountViewSet, basename="bank-accounts")
router.register(r"transactions", TransactionViewSet, basename="transactions")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "sync/all/",
        BankingSyncViewSet.as_view({"post": "sync_all_accounts"}),
        name="sync-all-accounts",
    ),
]