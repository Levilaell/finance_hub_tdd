import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal
from django.utils import timezone
from apps.banking.services.banking import BankingService, BankingServiceError
from apps.banking.models import BankProvider, BankAccount, Transaction
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
def banking_service():
    with patch('apps.banking.services.banking.PluggyClient') as mock_pluggy:
        service = BankingService()
        service.pluggy_client = mock_pluggy
        return service


class TestBankingService:
    """Test suite for Banking Service"""

    @pytest.mark.django_db
    def test_banking_service_initialization(self):
        """Should initialize banking service with Pluggy client"""
        service = BankingService()
        
        assert service.pluggy_client is not None
        assert hasattr(service, 'pluggy_client')

    @pytest.mark.django_db
    @patch('apps.banking.services.banking.PluggyClient')
    def test_sync_bank_providers(self, mock_pluggy_class, banking_service):
        """Should sync bank providers from Pluggy"""
        # Setup mock
        mock_pluggy = Mock()
        mock_pluggy_class.return_value = mock_pluggy
        mock_pluggy.authenticate.return_value = None
        mock_pluggy.get_connectors.return_value = [
            {
                "id": "bb_connector",
                "name": "Banco do Brasil",
                "code": "001",
                "primaryColor": "#FFF000",
                "institutionUrl": "https://bb.com.br",
                "country": "BR",
                "type": "PERSONAL_BANK",
                "credentials": [
                    {"name": "user", "type": "text"},
                    {"name": "password", "type": "password"}
                ]
            },
            {
                "id": "itau_connector",
                "name": "Itaú",
                "code": "341",
                "primaryColor": "#EC7000",
                "institutionUrl": "https://itau.com.br",
                "country": "BR",
                "type": "PERSONAL_BANK",
                "credentials": [
                    {"name": "user", "type": "text"},
                    {"name": "password", "type": "password"}
                ]
            }
        ]

        service = BankingService()
        result = service.sync_bank_providers()

        # Verify providers were created
        assert BankProvider.objects.count() == 2
        
        bb_provider = BankProvider.objects.get(pluggy_connector_id="bb_connector")
        assert bb_provider.name == "Banco do Brasil"
        assert bb_provider.is_active is True

        itau_provider = BankProvider.objects.get(pluggy_connector_id="itau_connector")
        assert itau_provider.name == "Itaú"
        
        assert result["created"] == 2
        assert result["updated"] == 0

    @pytest.mark.django_db
    @patch('apps.banking.services.banking.PluggyClient')
    def test_connect_bank_account(self, mock_pluggy_class, company, bank_provider):
        """Should connect a bank account via Pluggy"""
        # Setup mock
        mock_pluggy = Mock()
        mock_pluggy_class.return_value = mock_pluggy
        mock_pluggy.authenticate.return_value = None
        mock_pluggy.create_item.return_value = {
            "id": "item_123",
            "connector": {"id": "bb-connector-id", "name": "Banco do Brasil"},
            "status": "UPDATING",
            "executionStatus": "CREATED",
            "createdAt": "2024-01-01T10:00:00Z"
        }

        service = BankingService()
        credentials = {
            "user": "12345678",
            "password": "senha123"
        }

        result = service.connect_bank_account(company, bank_provider, credentials)

        # Verify item was created
        mock_pluggy.create_item.assert_called_once_with(
            "bb-connector-id", credentials
        )
        
        assert result["item_id"] == "item_123"
        assert result["status"] == "UPDATING"

    @pytest.mark.django_db
    @patch('apps.banking.services.banking.PluggyClient')
    def test_sync_bank_accounts(self, mock_pluggy_class, company, bank_provider):
        """Should sync bank accounts from Pluggy item"""
        # Setup mock
        mock_pluggy = Mock()
        mock_pluggy_class.return_value = mock_pluggy
        mock_pluggy.authenticate.return_value = None
        mock_pluggy.get_accounts.return_value = [
            {
                "id": "account_456",
                "type": "CHECKING",
                "subtype": "CHECKING_ACCOUNT",
                "name": "Conta Corrente",
                "balance": 1500.50,
                "currencyCode": "BRL",
                "itemId": "item_123",
                "number": "12345-6",
                "marketingName": "Conta Corrente Pessoa Física"
            },
            {
                "id": "account_789",
                "type": "SAVINGS",
                "subtype": "SAVINGS_ACCOUNT",
                "name": "Conta Poupança",
                "balance": 2000.00,
                "currencyCode": "BRL",
                "itemId": "item_123",
                "number": "12345-7",
                "marketingName": "Conta Poupança"
            }
        ]

        service = BankingService()
        result = service.sync_bank_accounts(company, bank_provider, "item_123")

        # Verify accounts were created
        assert BankAccount.objects.filter(company=company).count() == 2
        
        checking = BankAccount.objects.get(pluggy_account_id="account_456")
        assert checking.account_type == "CHECKING"
        assert checking.name == "Conta Corrente"
        assert checking.balance == Decimal("1500.50")
        assert checking.agency == ""  # Not provided in Pluggy response
        assert checking.account_number == "12345-6"

        savings = BankAccount.objects.get(pluggy_account_id="account_789")
        assert savings.account_type == "SAVINGS"
        assert savings.balance == Decimal("2000.00")
        
        assert result["created"] == 2
        assert result["updated"] == 0

    @pytest.mark.django_db
    @patch('apps.banking.services.banking.PluggyClient')
    def test_sync_transactions(self, mock_pluggy_class, company, bank_provider):
        """Should sync transactions from Pluggy account"""
        # Create bank account first
        bank_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Corrente",
            balance=Decimal("1000.00"),
        )

        # Setup mock
        mock_pluggy = Mock()
        mock_pluggy_class.return_value = mock_pluggy
        mock_pluggy.authenticate.return_value = None
        mock_pluggy.get_transactions.return_value = [
            {
                "id": "trans_789",
                "accountId": "account_456",
                "date": "2024-01-15",
                "description": "Compra Mercado",
                "amount": -150.00,
                "balance": 1350.50,
                "category": "Food & Dining",
                "providerCode": "DEBIT_PURCHASE"
            },
            {
                "id": "trans_790",
                "accountId": "account_456",
                "date": "2024-01-16",
                "description": "Depósito",
                "amount": 500.00,
                "balance": 1850.50,
                "category": "Transfer",
                "providerCode": "DEPOSIT"
            }
        ]

        service = BankingService()
        result = service.sync_transactions(
            bank_account,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31)
        )

        # Verify transactions were created
        assert Transaction.objects.filter(bank_account=bank_account).count() == 2
        
        debit_trans = Transaction.objects.get(pluggy_transaction_id="trans_789")
        assert debit_trans.transaction_type == "DEBIT"
        assert debit_trans.amount == Decimal("150.00")  # Absolute value
        assert debit_trans.description == "Compra Mercado"
        assert debit_trans.category == "Food & Dining"
        assert debit_trans.transaction_date == date(2024, 1, 15)

        credit_trans = Transaction.objects.get(pluggy_transaction_id="trans_790")
        assert credit_trans.transaction_type == "CREDIT"
        assert credit_trans.amount == Decimal("500.00")
        assert credit_trans.description == "Depósito"
        
        assert result["created"] == 2
        assert result["updated"] == 0

    @pytest.mark.django_db
    def test_update_existing_bank_account(self, company, bank_provider):
        """Should update existing bank account on sync"""
        # Create existing account
        existing_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Old Name",
            balance=Decimal("500.00"),
        )

        with patch('apps.banking.services.banking.PluggyClient') as mock_pluggy_class:
            mock_pluggy = Mock()
            mock_pluggy_class.return_value = mock_pluggy
            mock_pluggy.authenticate.return_value = None
            mock_pluggy.get_accounts.return_value = [
                {
                    "id": "account_456",
                    "type": "CHECKING",
                    "name": "Updated Name",
                    "balance": 1500.50,
                    "currencyCode": "BRL",
                    "itemId": "item_123",
                    "number": "12345-6",
                }
            ]

            service = BankingService()
            result = service.sync_bank_accounts(company, bank_provider, "item_123")

            # Verify account was updated
            existing_account.refresh_from_db()
            assert existing_account.name == "Updated Name"
            assert existing_account.balance == Decimal("1500.50")
            assert existing_account.account_number == "12345-6"
            
            assert result["created"] == 0
            assert result["updated"] == 1

    @pytest.mark.django_db
    def test_get_connection_status(self, banking_service):
        """Should get connection status from Pluggy"""
        banking_service.pluggy_client.get_item_status.return_value = {
            "id": "item_123",
            "status": "UPDATED",
            "executionStatus": "SUCCESS",
            "lastUpdatedAt": "2024-01-01T10:05:00Z"
        }

        status = banking_service.get_connection_status("item_123")

        banking_service.pluggy_client.get_item_status.assert_called_once_with("item_123")
        assert status["status"] == "UPDATED"
        assert status["executionStatus"] == "SUCCESS"

    @pytest.mark.django_db
    def test_disconnect_bank_account(self, company, bank_provider, banking_service):
        """Should disconnect bank account and delete from Pluggy"""
        # Create bank account
        bank_account = BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id="item_123",
            pluggy_account_id="account_456",
            account_type="CHECKING",
            name="Conta Test",
        )

        banking_service.disconnect_bank_account(bank_account)

        # Verify Pluggy item was deleted
        banking_service.pluggy_client.delete_item.assert_called_once_with("item_123")
        
        # Verify account was deactivated (not deleted to preserve transaction history)
        bank_account.refresh_from_db()
        assert bank_account.is_active is False

    @pytest.mark.django_db
    def test_handle_pluggy_errors(self, banking_service):
        """Should handle Pluggy API errors appropriately"""
        from apps.banking.services.pluggy import PluggyError
        
        banking_service.pluggy_client.get_connectors.side_effect = PluggyError("API Error")

        with pytest.raises(BankingServiceError) as exc_info:
            banking_service.sync_bank_providers()

        assert "Failed to sync bank providers" in str(exc_info.value)

    @pytest.mark.django_db
    def test_determine_transaction_type(self, banking_service):
        """Should correctly determine transaction type from amount"""
        # Test debit transaction (negative amount)
        trans_type = banking_service._determine_transaction_type(-100.00)
        assert trans_type == "DEBIT"

        # Test credit transaction (positive amount)
        trans_type = banking_service._determine_transaction_type(200.00)
        assert trans_type == "CREDIT"

        # Test zero amount (treated as debit)
        trans_type = banking_service._determine_transaction_type(0.00)
        assert trans_type == "DEBIT"

    @pytest.mark.django_db
    def test_map_account_type(self, banking_service):
        """Should map Pluggy account types to internal types"""
        assert banking_service._map_account_type("CHECKING") == "CHECKING"
        assert banking_service._map_account_type("SAVINGS") == "SAVINGS"
        assert banking_service._map_account_type("CREDIT_CARD") == "CREDIT_CARD"
        assert banking_service._map_account_type("INVESTMENT") == "CHECKING"  # Default

    @pytest.mark.django_db
    def test_full_sync_workflow(self, company, banking_service):
        """Should handle complete sync workflow"""
        # Setup comprehensive mock responses
        banking_service.pluggy_client.get_connectors.return_value = [
            {
                "id": "bb_connector",
                "name": "Banco do Brasil",
                "type": "PERSONAL_BANK"
            }
        ]
        
        banking_service.pluggy_client.create_item.return_value = {
            "id": "item_123",
            "status": "UPDATING"
        }
        
        banking_service.pluggy_client.get_accounts.return_value = [
            {
                "id": "account_456",
                "type": "CHECKING",
                "name": "Conta Corrente",
                "balance": 1000.00,
                "itemId": "item_123"
            }
        ]
        
        banking_service.pluggy_client.get_transactions.return_value = [
            {
                "id": "trans_789",
                "accountId": "account_456",
                "date": "2024-01-15",
                "description": "Test Transaction",
                "amount": -50.00,
                "category": "Shopping"
            }
        ]

        # Execute workflow
        providers_result = banking_service.sync_bank_providers()
        
        bank_provider = BankProvider.objects.first()
        connect_result = banking_service.connect_bank_account(
            company, bank_provider, {"user": "test", "password": "test"}
        )
        
        accounts_result = banking_service.sync_bank_accounts(
            company, bank_provider, "item_123"
        )
        
        bank_account = BankAccount.objects.first()
        transactions_result = banking_service.sync_transactions(bank_account)

        # Verify complete workflow
        assert providers_result["created"] == 1
        assert connect_result["item_id"] == "item_123"
        assert accounts_result["created"] == 1
        assert transactions_result["created"] == 1
        
        assert BankProvider.objects.count() == 1
        assert BankAccount.objects.count() == 1
        assert Transaction.objects.count() == 1