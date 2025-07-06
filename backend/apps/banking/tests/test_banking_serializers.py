import pytest
from decimal import Decimal
from datetime import date, datetime
from django.test import TestCase
from apps.banking.models import BankProvider, BankAccount, Transaction
from apps.banking.serializers import (
    BankProviderSerializer,
    BankAccountSerializer,
    TransactionSerializer,
    BankAccountCreateSerializer,
)
from apps.companies.models import Company
from apps.authentication.models import User


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
        name="Test Company", cnpj="11.222.333/0001-81", owner=user
    )


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
        is_active=True,
    )


@pytest.fixture
def transaction(bank_account):
    return Transaction.objects.create(
        bank_account=bank_account,
        pluggy_transaction_id="trans_789",
        transaction_type="DEBIT",
        amount=Decimal("250.75"),
        description="Compra no supermercado",
        transaction_date=date(2024, 1, 15),
        posted_date=date(2024, 1, 16),
        category="Alimentação",
        subcategory="Supermercado",
        is_pending=False,
    )


class TestBankProviderSerializer(TestCase):
    def test_serialize_bank_provider(self):
        """Should serialize bank provider correctly"""
        bank_provider = BankProvider.objects.create(
            name="Banco do Brasil",
            code="bb",
            pluggy_connector_id="bb-connector",
            logo_url="https://example.com/bb-logo.png",
            supports_checking_account=True,
            supports_savings_account=True,
            supports_credit_card=False,
        )

        serializer = BankProviderSerializer(bank_provider)
        data = serializer.data

        assert data["id"] == bank_provider.id
        assert data["name"] == "Banco do Brasil"
        assert data["code"] == "bb"
        assert data["pluggy_connector_id"] == "bb-connector"
        assert data["logo_url"] == "https://example.com/bb-logo.png"
        assert data["is_active"] is True
        assert data["supports_checking_account"] is True
        assert data["supports_savings_account"] is True
        assert data["supports_credit_card"] is False

    def test_serialize_multiple_bank_providers(self):
        """Should serialize multiple bank providers"""
        BankProvider.objects.create(
            name="Banco do Brasil", code="bb", pluggy_connector_id="bb-connector"
        )
        BankProvider.objects.create(
            name="Itaú", code="itau", pluggy_connector_id="itau-connector"
        )

        providers = BankProvider.objects.all()
        serializer = BankProviderSerializer(providers, many=True)
        data = serializer.data

        assert len(data) == 2
        assert data[0]["name"] == "Banco do Brasil"
        assert data[1]["name"] == "Itaú"


class TestBankAccountSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
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
            agency="1234",
            account_number="567890",
            balance=Decimal("1500.50"),
        )

    def test_serialize_bank_account(self):
        """Should serialize bank account with nested provider"""
        serializer = BankAccountSerializer(self.bank_account)
        data = serializer.data

        assert data["id"] == self.bank_account.id
        assert data["company"] == self.company.id
        assert data["bank_provider"]["id"] == self.bank_provider.id
        assert data["bank_provider"]["name"] == "Banco do Brasil"
        assert data["pluggy_item_id"] == "item_123"
        assert data["pluggy_account_id"] == "account_456"
        assert data["account_type"] == "CHECKING"
        assert data["name"] == "Conta Corrente"
        assert data["agency"] == "1234"
        assert data["account_number"] == "567890"
        assert data["balance"] == "1500.50"
        assert data["is_active"] is True

    def test_serialize_bank_account_with_transactions_count(self):
        """Should include transaction count in serialization"""
        # Create some transactions
        Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Test transaction 1",
            transaction_date=date.today(),
        )
        Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="Test transaction 2",
            transaction_date=date.today(),
        )

        serializer = BankAccountSerializer(self.bank_account)
        data = serializer.data

        assert data["transactions_count"] == 2


class TestBankAccountCreateSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.bank_provider = BankProvider.objects.create(
            name="Banco do Brasil", code="bb", pluggy_connector_id="bb-connector"
        )

    def test_create_bank_account_valid_data(self):
        """Should create bank account with valid data"""
        data = {
            "company": self.company.id,
            "bank_provider": self.bank_provider.id,
            "pluggy_item_id": "item_123",
            "pluggy_account_id": "account_456",
            "account_type": "CHECKING",
            "name": "Conta Corrente",
            "agency": "1234",
            "account_number": "567890",
            "balance": "1500.50",
        }

        serializer = BankAccountCreateSerializer(data=data)
        assert serializer.is_valid()

        bank_account = serializer.save()
        assert bank_account.company == self.company
        assert bank_account.bank_provider == self.bank_provider
        assert bank_account.pluggy_item_id == "item_123"
        assert bank_account.account_type == "CHECKING"
        assert bank_account.balance == Decimal("1500.50")

    def test_create_bank_account_invalid_account_type(self):
        """Should reject invalid account type"""
        data = {
            "company": self.company.id,
            "bank_provider": self.bank_provider.id,
            "pluggy_item_id": "item_123",
            "pluggy_account_id": "account_456",
            "account_type": "INVALID_TYPE",
            "name": "Conta Corrente",
        }

        serializer = BankAccountCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "account_type" in serializer.errors

    def test_create_bank_account_duplicate_pluggy_account_id(self):
        """Should reject duplicate pluggy_account_id"""
        # Create first account
        BankAccount.objects.create(
            company=self.company,
            bank_provider=self.bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Primeira Conta",
        )

        # Try to create second account with same pluggy_account_id
        data = {
            "company": self.company.id,
            "bank_provider": self.bank_provider.id,
            "pluggy_item_id": "item_789",
            "pluggy_account_id": "account_456",  # Same as first
            "account_type": "SAVINGS",
            "name": "Segunda Conta",
        }

        serializer = BankAccountCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "pluggy_account_id" in serializer.errors


class TestTransactionSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
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

    def test_serialize_transaction(self):
        """Should serialize transaction correctly"""
        transaction = Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_789",
            transaction_type="DEBIT",
            amount=Decimal("250.75"),
            description="Compra no supermercado",
            transaction_date=date(2024, 1, 15),
            posted_date=date(2024, 1, 16),
            category="Alimentação",
            subcategory="Supermercado",
            is_pending=False,
        )

        serializer = TransactionSerializer(transaction)
        data = serializer.data

        assert data["id"] == transaction.id
        assert data["bank_account"] == self.bank_account.id
        assert data["pluggy_transaction_id"] == "trans_789"
        assert data["transaction_type"] == "DEBIT"
        assert data["amount"] == "250.75"
        assert data["description"] == "Compra no supermercado"
        assert data["transaction_date"] == "2024-01-15"
        assert data["posted_date"] == "2024-01-16"
        assert data["category"] == "Alimentação"
        assert data["subcategory"] == "Supermercado"
        assert data["is_pending"] is False

    def test_serialize_transaction_with_bank_account_details(self):
        """Should include bank account details in transaction serialization"""
        transaction = Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_789",
            transaction_type="CREDIT",
            amount=Decimal("1000.00"),
            description="Depósito",
            transaction_date=date.today(),
        )

        serializer = TransactionSerializer(transaction)
        data = serializer.data

        assert "bank_account_details" in data
        assert data["bank_account_details"]["name"] == "Conta Corrente"
        assert data["bank_account_details"]["bank_provider_name"] == "Banco do Brasil"

    def test_serialize_pending_transaction(self):
        """Should serialize pending transaction correctly"""
        transaction = Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_pending",
            transaction_type="DEBIT",
            amount=Decimal("50.00"),
            description="Compra pendente",
            transaction_date=date.today(),
            is_pending=True,
        )

        serializer = TransactionSerializer(transaction)
        data = serializer.data

        assert data["is_pending"] is True
        assert data["posted_date"] is None

    def test_serialize_multiple_transactions(self):
        """Should serialize multiple transactions with proper ordering"""
        Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Primeira transação",
            transaction_date=date(2024, 1, 10),
        )
        Transaction.objects.create(
            bank_account=self.bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="Segunda transação",
            transaction_date=date(2024, 1, 15),
        )

        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        data = serializer.data

        assert len(data) == 2
        # Should be ordered by transaction_date desc
        assert data[0]["transaction_date"] == "2024-01-15"
        assert data[1]["transaction_date"] == "2024-01-10"