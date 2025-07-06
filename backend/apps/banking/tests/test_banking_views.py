import pytest
from decimal import Decimal
from datetime import date, datetime
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.companies.models import Company, CompanyUser
from apps.banking.models import BankProvider, BankAccount, Transaction


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def company(user):
    return Company.objects.create(
        name="Test Company",
        cnpj="11.222.333/0001-81",
        owner=user,
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def bank_provider(db):
    return BankProvider.objects.create(
        name="Banco do Brasil",
        code="bb",
        pluggy_connector_id="bb-connector",
        logo_url="https://example.com/bb-logo.png",
        supports_checking_account=True,
        supports_savings_account=True,
        supports_credit_card=False,
    )


@pytest.fixture
def bank_account(company, bank_provider):
    return BankAccount.objects.create(
        company=company,
        bank_provider=bank_provider,
        pluggy_item_id="item_123",
        pluggy_account_id="account_456",
        account_type="CHECKING",
        name="Conta Corrente",
        agency="1234",
        account_number="567890",
        balance=Decimal("1500.50"),
    )


class TestBankProviderViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.client.force_authenticate(user=self.user)

        # Create test bank providers
        self.bb_provider = BankProvider.objects.create(
            name="Banco do Brasil",
            code="bb",
            pluggy_connector_id="bb-connector",
            supports_checking_account=True,
            supports_savings_account=True,
        )
        self.itau_provider = BankProvider.objects.create(
            name="Itaú",
            code="itau",
            pluggy_connector_id="itau-connector",
            supports_checking_account=True,
            supports_credit_card=True,
        )

    def test_list_bank_providers(self):
        """Should list all active bank providers"""
        url = reverse("banking:bank-providers-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Check ordering by name
        assert response.data["results"][0]["name"] == "Banco do Brasil"
        assert response.data["results"][1]["name"] == "Itaú"

    def test_list_bank_providers_only_active(self):
        """Should only list active bank providers"""
        # Deactivate one provider
        self.itau_provider.is_active = False
        self.itau_provider.save()

        url = reverse("banking:bank-providers-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Banco do Brasil"

    def test_retrieve_bank_provider(self):
        """Should retrieve specific bank provider"""
        url = reverse("banking:bank-providers-detail", kwargs={"pk": self.bb_provider.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Banco do Brasil"
        assert response.data["code"] == "bb"
        assert response.data["supports_checking_account"] is True

    def test_bank_provider_requires_authentication(self):
        """Should require authentication to access bank providers"""
        self.client.force_authenticate(user=None)
        url = reverse("banking:bank-providers-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestBankAccountViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        self.bank_provider = BankProvider.objects.create(
            name="Banco do Brasil", code="bb", pluggy_connector_id="bb-connector"
        )

        self.bank_account = BankAccount.objects.create(
            company=self.company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente",
            balance=Decimal("1500.50"),
        )

    def test_list_bank_accounts_for_company(self):
        """Should list bank accounts for user's company"""
        url = reverse("banking:bank-accounts-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Conta Corrente"
        assert response.data["results"][0]["balance"] == "1500.50"

    def test_list_bank_accounts_filters_by_company(self):
        """Should only show accounts for user's company"""
        # Create another company and account
        other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123!"
        )
        other_company = Company.objects.create(
            name="Other Company", cnpj="22.333.444/0001-82", owner=other_user
        )
        BankAccount.objects.create(
            company=other_company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_789",
            pluggy_account_id="account_789",
            account_type="SAVINGS",
            name="Other Account",
        )

        url = reverse("banking:bank-accounts-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Conta Corrente"

    def test_create_bank_account(self):
        """Should create new bank account"""
        url = reverse("banking:bank-accounts-list")
        data = {
            "company": self.company.id,
            "bank_provider": self.bank_provider.id,
            "pluggy_item_id": "item_new",
            "pluggy_account_id": "account_new",
            "account_type": "SAVINGS",
            "name": "Nova Conta Poupança",
            "agency": "5678",
            "account_number": "123456",
            "balance": "2500.75",
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Nova Conta Poupança"
        assert response.data["account_type"] == "SAVINGS"
        assert response.data["balance"] == "2500.75"

        # Verify account was created in database
        assert BankAccount.objects.filter(pluggy_account_id="account_new").exists()

    def test_retrieve_bank_account(self):
        """Should retrieve specific bank account"""
        url = reverse("banking:bank-accounts-detail", kwargs={"pk": self.bank_account.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Conta Corrente"
        assert response.data["bank_provider"]["name"] == "Banco do Brasil"

    def test_update_bank_account(self):
        """Should update bank account"""
        url = reverse("banking:bank-accounts-detail", kwargs={"pk": self.bank_account.pk})
        data = {
            "name": "Conta Corrente Atualizada",
            "balance": "2000.00",
        }

        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Conta Corrente Atualizada"
        assert response.data["balance"] == "2000.00"

    def test_delete_bank_account(self):
        """Should delete bank account"""
        url = reverse("banking:bank-accounts-detail", kwargs={"pk": self.bank_account.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BankAccount.objects.filter(pk=self.bank_account.pk).exists()

    def test_bank_account_requires_company_access(self):
        """Should require user to have access to company"""
        # Create user without company access
        other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123!"
        )
        self.client.force_authenticate(user=other_user)

        url = reverse("banking:bank-accounts-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


class TestTransactionViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        self.bank_provider = BankProvider.objects.create(
            name="Banco do Brasil", code="bb", pluggy_connector_id="bb-connector"
        )
        self.bank_account = BankAccount.objects.create(
            company=self.company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente",
        )

        # Create test transactions
        self.transaction1 = Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("250.75"),
            description="Compra supermercado",
            transaction_date=date(2024, 1, 15),
            category="Alimentação",
        )
        self.transaction2 = Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("1000.00"),
            description="Salário",
            transaction_date=date(2024, 1, 10),
            category="Receita",
        )

    def test_list_transactions_for_user_accounts(self):
        """Should list transactions for user's bank accounts"""
        url = reverse("banking:transactions-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Should be ordered by transaction_date desc
        assert response.data["results"][0]["description"] == "Compra supermercado"
        assert response.data["results"][1]["description"] == "Salário"

    def test_filter_transactions_by_account(self):
        """Should filter transactions by bank account"""
        url = reverse("banking:transactions-list")
        response = self.client.get(url, {"bank_account": self.bank_account.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_transactions_by_type(self):
        """Should filter transactions by type"""
        url = reverse("banking:transactions-list")
        response = self.client.get(url, {"transaction_type": "DEBIT"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["transaction_type"] == "DEBIT"

    def test_filter_transactions_by_date_range(self):
        """Should filter transactions by date range"""
        url = reverse("banking:transactions-list")
        response = self.client.get(
            url, {"date_from": "2024-01-12", "date_to": "2024-01-16"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["description"] == "Compra supermercado"

    def test_search_transactions_by_description(self):
        """Should search transactions by description"""
        url = reverse("banking:transactions-list")
        response = self.client.get(url, {"search": "supermercado"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["description"] == "Compra supermercado"

    def test_retrieve_transaction(self):
        """Should retrieve specific transaction"""
        url = reverse("banking:transactions-detail", kwargs={"pk": self.transaction1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "Compra supermercado"
        assert response.data["bank_account_details"]["name"] == "Conta Corrente"

    def test_transactions_filters_by_company_accounts(self):
        """Should only show transactions for user's company accounts"""
        # Create another company and transactions
        other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123!"
        )
        other_company = Company.objects.create(
            name="Other Company", cnpj="22.333.444/0001-82", owner=other_user
        )
        other_account = BankAccount.objects.create(
            company=other_company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_789",
            pluggy_account_id="account_789",
            account_type="SAVINGS",
            name="Other Account",
        )
        Transaction.objects.create(
            bank_account=other_account,
            pluggy_transaction_id="trans_other",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Other transaction",
            transaction_date=date.today(),
        )

        url = reverse("banking:transactions-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Only user's transactions

    def test_transaction_requires_authentication(self):
        """Should require authentication to access transactions"""
        self.client.force_authenticate(user=None)
        url = reverse("banking:transactions-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestBankingSyncViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        self.bank_provider = BankProvider.objects.create(
            name="Banco do Brasil", code="bb", pluggy_connector_id="bb-connector"
        )
        self.bank_account = BankAccount.objects.create(
            company=self.company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente",
        )

    def test_sync_account_transactions(self):
        """Should trigger sync for specific account"""
        url = reverse(
            "banking:bank-accounts-sync", kwargs={"pk": self.bank_account.pk}
        )
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "task_id" in response.data

    def test_sync_all_company_accounts(self):
        """Should trigger sync for all company accounts"""
        url = reverse("banking:sync-all-accounts")
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "task_id" in response.data