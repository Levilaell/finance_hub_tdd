from django.test import TestCase
from django.urls import reverse, resolve
from apps.banking.views import (
    BankProviderViewSet,
    BankAccountViewSet,
    TransactionViewSet,
    BankingSyncViewSet,
)


class TestBankingURLs(TestCase):
    """Test Banking URL patterns"""

    def test_bank_providers_list_url(self):
        """Should resolve bank providers list URL"""
        url = reverse("banking:bank-providers-list")
        assert url == "/api/banking/providers/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankProviderViewSet
        assert resolver.url_name == "bank-providers-list"

    def test_bank_providers_detail_url(self):
        """Should resolve bank providers detail URL"""
        url = reverse("banking:bank-providers-detail", kwargs={"pk": 1})
        assert url == "/api/banking/providers/1/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankProviderViewSet
        assert resolver.url_name == "bank-providers-detail"

    def test_bank_accounts_list_url(self):
        """Should resolve bank accounts list URL"""
        url = reverse("banking:bank-accounts-list")
        assert url == "/api/banking/accounts/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankAccountViewSet
        assert resolver.url_name == "bank-accounts-list"

    def test_bank_accounts_detail_url(self):
        """Should resolve bank accounts detail URL"""
        url = reverse("banking:bank-accounts-detail", kwargs={"pk": 1})
        assert url == "/api/banking/accounts/1/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankAccountViewSet
        assert resolver.url_name == "bank-accounts-detail"

    def test_bank_accounts_sync_url(self):
        """Should resolve bank accounts sync URL"""
        url = reverse("banking:bank-accounts-sync", kwargs={"pk": 1})
        assert url == "/api/banking/accounts/1/sync/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankAccountViewSet
        assert resolver.url_name == "bank-accounts-sync"

    def test_transactions_list_url(self):
        """Should resolve transactions list URL"""
        url = reverse("banking:transactions-list")
        assert url == "/api/banking/transactions/"
        
        resolver = resolve(url)
        assert resolver.func.cls == TransactionViewSet
        assert resolver.url_name == "transactions-list"

    def test_transactions_detail_url(self):
        """Should resolve transactions detail URL"""
        url = reverse("banking:transactions-detail", kwargs={"pk": 1})
        assert url == "/api/banking/transactions/1/"
        
        resolver = resolve(url)
        assert resolver.func.cls == TransactionViewSet
        assert resolver.url_name == "transactions-detail"

    def test_sync_all_accounts_url(self):
        """Should resolve sync all accounts URL"""
        url = reverse("banking:sync-all-accounts")
        assert url == "/api/banking/sync/all/"
        
        resolver = resolve(url)
        assert resolver.func.cls == BankingSyncViewSet