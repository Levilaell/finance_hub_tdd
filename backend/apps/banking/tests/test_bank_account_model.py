import pytest
from django.db import IntegrityError
from decimal import Decimal
from apps.banking.models import BankAccount, BankProvider
from apps.companies.models import Company, CompanyUser
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
        name="Test Company",
        cnpj="11.222.333/0001-81",
        owner=user,
    )


@pytest.fixture
def bank_provider(db):
    return BankProvider.objects.create(
        name="Banco do Brasil",
        code="001",
        pluggy_connector_id="bb-connector-id",
    )


class TestBankAccountModel:
    """Test suite for BankAccount model"""

    @pytest.mark.django_db
    def test_create_bank_account(self, company, bank_provider):
        """Should create a bank account with required fields"""
        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente BB",
            agency="1234",
            account_number="56789-0",
            balance=Decimal("1000.00"),
        )

        assert account.company == company
        assert account.bank_provider == bank_provider
        assert account.pluggy_item_id == "item_123"
        assert account.pluggy_account_id == "account_456"
        assert account.account_type == "CHECKING"
        assert account.name == "Conta Corrente BB"
        assert account.agency == "1234"
        assert account.account_number == "56789-0"
        assert account.balance == Decimal("1000.00")
        assert account.is_active is True
        assert account.last_sync is None
        assert account.created_at is not None
        assert account.updated_at is not None

    @pytest.mark.django_db
    def test_bank_account_str_representation(self, company, bank_provider):
        """Should return formatted string representation"""
        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente BB",
        )

        assert str(account) == "Conta Corrente BB - Banco do Brasil"

    @pytest.mark.django_db
    def test_bank_account_types(self, company, bank_provider):
        """Should support different account types"""
        checking = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_1",
            pluggy_account_id="account_1",
            account_type="CHECKING",
            name="Conta Corrente",
        )

        savings = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_2",
            pluggy_account_id="account_2",
            account_type="SAVINGS",
            name="Conta Poupança",
        )

        credit_card = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_3",
            pluggy_account_id="account_3",
            account_type="CREDIT_CARD",
            name="Cartão de Crédito",
        )

        assert checking.account_type == "CHECKING"
        assert savings.account_type == "SAVINGS"
        assert credit_card.account_type == "CREDIT_CARD"

    @pytest.mark.django_db
    def test_bank_account_unique_pluggy_account_id(self, company, bank_provider):
        """Should enforce unique pluggy account id constraint"""
        BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta 1",
        )

        with pytest.raises(IntegrityError):
            BankAccount.objects.create(
                company=company,
                bank_provider=bank_provider,
                pluggy_item_id="item_789",
                pluggy_account_id="account_456",  # Same account id
                account_type="CHECKING",
                name="Conta 2",
            )

    @pytest.mark.django_db
    def test_bank_account_default_values(self, company, bank_provider):
        """Should set default values correctly"""
        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Test",
        )

        assert account.balance == Decimal("0.00")
        assert account.is_active is True
        assert account.last_sync is None

    @pytest.mark.django_db
    def test_bank_account_decimal_precision(self, company, bank_provider):
        """Should handle decimal values with proper precision"""
        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Test",
            balance=Decimal("12345.67"),
        )

        account.refresh_from_db()
        assert account.balance == Decimal("12345.67")

    @pytest.mark.django_db
    def test_bank_account_company_cascade_delete(self, company, bank_provider):
        """Should delete bank accounts when company is deleted"""
        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Test",
        )

        company.delete()

        assert BankAccount.objects.filter(id=account.id).exists() is False

    @pytest.mark.django_db
    def test_get_active_accounts_for_company(self, company, bank_provider):
        """Should filter active accounts for a company"""
        active_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_1",
            pluggy_account_id="account_1",
            account_type="CHECKING",
            name="Conta Ativa",
            is_active=True,
        )

        inactive_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_2",
            pluggy_account_id="account_2",
            account_type="CHECKING",
            name="Conta Inativa",
            is_active=False,
        )

        active_accounts = BankAccount.objects.filter(
            company=company, is_active=True
        )

        assert active_account in active_accounts
        assert inactive_account not in active_accounts
        assert active_accounts.count() == 1

    @pytest.mark.django_db
    def test_bank_account_ordering(self, company, bank_provider):
        """Should order bank accounts by created_at descending"""
        account1 = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_1",
            pluggy_account_id="account_1",
            account_type="CHECKING",
            name="Conta 1",
        )

        account2 = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_2",
            pluggy_account_id="account_2",
            account_type="SAVINGS",
            name="Conta 2",
        )

        accounts = BankAccount.objects.filter(company=company)
        assert list(accounts) == [account2, account1]  # Newer first

    @pytest.mark.django_db
    def test_update_last_sync_timestamp(self, company, bank_provider):
        """Should update last_sync timestamp"""
        from django.utils import timezone

        account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Test",
        )

        assert account.last_sync is None

        now = timezone.now()
        account.last_sync = now
        account.save()

        account.refresh_from_db()
        assert account.last_sync == now