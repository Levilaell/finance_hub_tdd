from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .permissions import IsBankAccountOwner, IsTransactionOwner
from .models import BankProvider, BankAccount, Transaction
from .serializers import (
    BankProviderSerializer,
    BankAccountSerializer,
    BankAccountCreateSerializer,
    TransactionSerializer,
)
from .filters import TransactionFilter
import uuid


class BankProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BankProvider - read-only"""

    queryset = BankProvider.objects.filter(is_active=True).order_by("name")
    serializer_class = BankProviderSerializer
    permission_classes = [IsAuthenticated]


class BankAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for BankAccount with company filtering"""

    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, IsBankAccountOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["account_type", "bank_provider", "is_active"]
    search_fields = ["name", "agency", "account_number"]

    def get_queryset(self):
        """Filter accounts by user's companies"""
        user_companies = self.request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        return BankAccount.objects.filter(company__in=user_companies).order_by(
            "-created_at"
        )

    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == "create":
            return BankAccountCreateSerializer
        return BankAccountSerializer

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        """Trigger sync for specific bank account"""
        bank_account = self.get_object()
        
        # Import here to avoid circular imports
        from .tasks import sync_account_transactions
        
        # Trigger async task
        task = sync_account_transactions.delay(bank_account.id)
        
        return Response(
            {
                "message": f"Sync initiated for account {bank_account.name}",
                "task_id": str(task.id),
            },
            status=status.HTTP_200_OK,
        )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Transaction - read-only with filtering"""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsTransactionOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ["description", "category", "subcategory"]

    def get_queryset(self):
        """Filter transactions by user's company bank accounts"""
        user_companies = self.request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        return Transaction.objects.filter(
            bank_account__company__in=user_companies
        ).order_by("-transaction_date", "-created_at")


class BankingSyncViewSet(viewsets.ViewSet):
    """ViewSet for banking sync operations"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def sync_all_accounts(self, request):
        """Trigger sync for all user's company accounts"""
        user_companies = request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        
        accounts = BankAccount.objects.filter(
            company__in=user_companies, is_active=True
        )
        
        if not accounts.exists():
            return Response(
                {"message": "No active bank accounts found to sync"},
                status=status.HTTP_200_OK,
            )
        
        # Import here to avoid circular imports
        from .tasks import sync_all_company_accounts
        
        # Trigger async task
        task = sync_all_company_accounts.delay(list(user_companies))
        
        return Response(
            {
                "message": f"Sync initiated for {accounts.count()} accounts",
                "task_id": str(task.id),
            },
            status=status.HTTP_200_OK,
        )