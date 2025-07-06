import pytest
from django.db import IntegrityError, models, transaction as db_transaction
from decimal import Decimal
from datetime import date, datetime
from django.utils import timezone
from apps.banking.models import Transaction, BankAccount, BankProvider
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


@pytest.fixture
def bank_account(company, bank_provider):
    return BankAccount.objects.create(
        company=company,
        bank_provider=bank_provider,
        pluggy_item_id="item_123",
        pluggy_account_id="account_456",
        account_type="CHECKING",
        name="Conta Corrente BB",
        balance=Decimal("1000.00"),
    )


class TestTransactionModel:
    """Test suite for Transaction model"""

    @pytest.mark.django_db
    def test_create_transaction(self, bank_account):
        """Should create a transaction with required fields"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Compra no Mercado",
            transaction_date=date(2024, 1, 15),
            posted_date=date(2024, 1, 16),
        )

        assert transaction.bank_account == bank_account
        assert transaction.pluggy_transaction_id == "trans_123"
        assert transaction.transaction_type == "DEBIT"
        assert transaction.amount == Decimal("100.00")
        assert transaction.description == "Compra no Mercado"
        assert transaction.transaction_date == date(2024, 1, 15)
        assert transaction.posted_date == date(2024, 1, 16)
        assert transaction.category == ""
        assert transaction.subcategory == ""
        assert transaction.is_pending is False
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    @pytest.mark.django_db
    def test_transaction_str_representation(self, bank_account):
        """Should return formatted string representation"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("150.50"),
            description="Restaurante",
            transaction_date=date(2024, 1, 20),
        )

        assert str(transaction) == "2024-01-20 - R$ 150.50 - Restaurante"

    @pytest.mark.django_db
    def test_transaction_types(self, bank_account):
        """Should support different transaction types"""
        debit = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Débito",
            transaction_date=date.today(),
        )

        credit = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="Crédito",
            transaction_date=date.today(),
        )

        assert debit.transaction_type == "DEBIT"
        assert credit.transaction_type == "CREDIT"

    @pytest.mark.django_db
    def test_transaction_unique_pluggy_id_per_account(self, bank_account, company, bank_provider):
        """Should enforce unique pluggy transaction id per account"""
        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Transaction 1",
            transaction_date=date.today(),
        )

        # Same transaction ID in same account should fail
        with pytest.raises(IntegrityError):
            with db_transaction.atomic():
                Transaction.objects.create(
                    bank_account=bank_account,
                    pluggy_transaction_id="trans_123",  # Same ID
                    transaction_type="CREDIT",
                    amount=Decimal("200.00"),
                    description="Transaction 2",
                    transaction_date=date.today(),
                )

        # Same transaction ID in different account should work
        other_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_789",
            pluggy_account_id="account_789",
            account_type="SAVINGS",
            name="Conta Poupança",
        )

        Transaction.objects.create(
            bank_account=other_account,
            pluggy_transaction_id="trans_123",  # Same ID, different account
            transaction_type="CREDIT",
            amount=Decimal("300.00"),
            description="Transaction 3",
            transaction_date=date.today(),
        )

    @pytest.mark.django_db
    def test_transaction_decimal_precision(self, bank_account):
        """Should handle decimal values with proper precision"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("1234.56"),
            description="Test",
            transaction_date=date.today(),
        )

        transaction.refresh_from_db()
        assert transaction.amount == Decimal("1234.56")

    @pytest.mark.django_db
    def test_transaction_pending_status(self, bank_account):
        """Should handle pending transactions"""
        pending = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Pending",
            transaction_date=date.today(),
            is_pending=True,
        )

        posted = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="Posted",
            transaction_date=date.today(),
            is_pending=False,
        )

        assert pending.is_pending is True
        assert posted.is_pending is False

    @pytest.mark.django_db
    def test_transaction_category_fields(self, bank_account):
        """Should allow optional category and subcategory"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Test",
            transaction_date=date.today(),
            category="Alimentação",
            subcategory="Restaurantes",
        )

        assert transaction.category == "Alimentação"
        assert transaction.subcategory == "Restaurantes"

    @pytest.mark.django_db
    def test_transaction_bank_account_cascade_delete(self, bank_account):
        """Should delete transactions when bank account is deleted"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Test",
            transaction_date=date.today(),
        )

        bank_account.delete()

        assert Transaction.objects.filter(id=transaction.id).exists() is False

    @pytest.mark.django_db
    def test_transaction_ordering(self, bank_account):
        """Should order transactions by transaction_date descending"""
        trans1 = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Old",
            transaction_date=date(2024, 1, 1),
        )

        trans2 = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="New",
            transaction_date=date(2024, 1, 15),
        )

        transactions = Transaction.objects.filter(bank_account=bank_account)
        assert list(transactions) == [trans2, trans1]  # Newer first

    @pytest.mark.django_db
    def test_get_transactions_by_date_range(self, bank_account):
        """Should filter transactions by date range"""
        trans1 = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="January",
            transaction_date=date(2024, 1, 15),
        )

        trans2 = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="CREDIT",
            amount=Decimal("200.00"),
            description="February",
            transaction_date=date(2024, 2, 15),
        )

        trans3 = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_3",
            transaction_type="DEBIT",
            amount=Decimal("300.00"),
            description="March",
            transaction_date=date(2024, 3, 15),
        )

        # Filter February transactions
        feb_transactions = Transaction.objects.filter(
            bank_account=bank_account,
            transaction_date__gte=date(2024, 2, 1),
            transaction_date__lt=date(2024, 3, 1),
        )

        assert feb_transactions.count() == 1
        assert trans2 in feb_transactions

    @pytest.mark.django_db
    def test_calculate_account_balance(self, bank_account):
        """Should calculate balance from transactions"""
        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_1",
            transaction_type="CREDIT",
            amount=Decimal("500.00"),
            description="Deposit",
            transaction_date=date.today(),
        )

        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_2",
            transaction_type="DEBIT",
            amount=Decimal("200.00"),
            description="Withdrawal",
            transaction_date=date.today(),
        )

        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_3",
            transaction_type="CREDIT",
            amount=Decimal("100.00"),
            description="Deposit",
            transaction_date=date.today(),
        )

        # Calculate balance
        credits = Transaction.objects.filter(
            bank_account=bank_account, transaction_type="CREDIT"
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        debits = Transaction.objects.filter(
            bank_account=bank_account, transaction_type="DEBIT"
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        balance = credits - debits
        assert balance == Decimal("400.00")  # 500 + 100 - 200

    @pytest.mark.django_db
    def test_optional_posted_date(self, bank_account):
        """Should allow posted_date to be optional"""
        transaction = Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id="trans_123",
            transaction_type="DEBIT",
            amount=Decimal("100.00"),
            description="Test",
            transaction_date=date.today(),
            # posted_date not provided
        )

        assert transaction.posted_date is None

        # Update with posted date
        transaction.posted_date = date.today()
        transaction.save()

        transaction.refresh_from_db()
        assert transaction.posted_date == date.today()