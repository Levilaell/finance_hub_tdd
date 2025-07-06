import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal
import requests
from apps.banking.services.pluggy import PluggyClient, PluggyError


class TestPluggyClient:
    """Test suite for Pluggy API client"""

    @pytest.fixture
    def pluggy_client(self):
        return PluggyClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            sandbox=True
        )

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object"""
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {}
        return mock

    @pytest.mark.django_db
    def test_pluggy_client_initialization(self):
        """Should initialize client with credentials"""
        client = PluggyClient(
            client_id="my_client_id",
            client_secret="my_client_secret",
            sandbox=True
        )

        assert client.client_id == "my_client_id"
        assert client.client_secret == "my_client_secret"
        assert client.sandbox is True
        assert client.base_url == "https://api.sandbox.pluggy.ai"
        assert client.api_key is None

    @pytest.mark.django_db
    def test_pluggy_client_production_url(self):
        """Should use production URL when sandbox is False"""
        client = PluggyClient(
            client_id="my_client_id",
            client_secret="my_client_secret",
            sandbox=False
        )

        assert client.base_url == "https://api.pluggy.ai"

    @pytest.mark.django_db
    @patch('requests.post')
    def test_authenticate(self, mock_post, pluggy_client):
        """Should authenticate and store API key"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"apiKey": "test_api_key_123"}
        mock_post.return_value = mock_response

        pluggy_client.authenticate()

        mock_post.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/auth",
            json={
                "clientId": "test_client_id",
                "clientSecret": "test_client_secret"
            },
            headers={"Content-Type": "application/json"}
        )
        assert pluggy_client.api_key == "test_api_key_123"

    @pytest.mark.django_db
    @patch('requests.post')
    def test_authenticate_failure(self, mock_post, pluggy_client):
        """Should raise PluggyError on authentication failure"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid credentials"}
        mock_post.return_value = mock_response

        with pytest.raises(PluggyError) as exc_info:
            pluggy_client.authenticate()

        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.django_db
    @patch('requests.get')
    def test_get_connectors(self, mock_get, pluggy_client):
        """Should retrieve list of bank connectors"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "bb_connector",
                    "name": "Banco do Brasil",
                    "primaryColor": "#FFF000",
                    "institutionUrl": "https://bb.com.br",
                    "country": "BR",
                    "type": "PERSONAL_BANK",
                    "credentials": [
                        {"name": "user", "type": "text"},
                        {"name": "password", "type": "password"}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        connectors = pluggy_client.get_connectors()

        mock_get.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/connectors",
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert len(connectors) == 1
        assert connectors[0]["id"] == "bb_connector"
        assert connectors[0]["name"] == "Banco do Brasil"

    @pytest.mark.django_db
    @patch('requests.post')
    def test_create_item(self, mock_post, pluggy_client):
        """Should create a new connection item"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "item_123",
            "connector": {"id": "bb_connector", "name": "Banco do Brasil"},
            "status": "UPDATING",
            "executionStatus": "CREATED",
            "createdAt": "2024-01-01T10:00:00Z"
        }
        mock_post.return_value = mock_response

        parameters = {
            "user": "12345678",
            "password": "senha123"
        }

        item = pluggy_client.create_item("bb_connector", parameters)

        mock_post.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/items",
            json={
                "connectorId": "bb_connector",
                "parameters": parameters
            },
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert item["id"] == "item_123"
        assert item["status"] == "UPDATING"

    @pytest.mark.django_db
    @patch('requests.get')
    def test_get_item_status(self, mock_get, pluggy_client):
        """Should get item connection status"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "item_123",
            "status": "UPDATED",
            "executionStatus": "SUCCESS",
            "lastUpdatedAt": "2024-01-01T10:05:00Z"
        }
        mock_get.return_value = mock_response

        status = pluggy_client.get_item_status("item_123")

        mock_get.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/items/item_123",
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert status["status"] == "UPDATED"
        assert status["executionStatus"] == "SUCCESS"

    @pytest.mark.django_db
    @patch('requests.get')
    def test_get_accounts(self, mock_get, pluggy_client):
        """Should retrieve accounts for an item"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
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
                }
            ]
        }
        mock_get.return_value = mock_response

        accounts = pluggy_client.get_accounts("item_123")

        mock_get.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/accounts",
            params={"itemId": "item_123"},
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert len(accounts) == 1
        assert accounts[0]["id"] == "account_456"
        assert accounts[0]["balance"] == 1500.50

    @pytest.mark.django_db
    @patch('requests.get')
    def test_get_transactions(self, mock_get, pluggy_client):
        """Should retrieve transactions for an account"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "trans_789",
                    "accountId": "account_456",
                    "date": "2024-01-15",
                    "description": "Compra Mercado",
                    "amount": -150.00,
                    "balance": 1350.50,
                    "category": "Food & Dining",
                    "providerCode": "DEBIT_PURCHASE"
                }
            ],
            "page": 1,
            "totalPages": 1,
            "total": 1
        }
        mock_get.return_value = mock_response

        transactions = pluggy_client.get_transactions(
            "account_456",
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31)
        )

        mock_get.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/transactions",
            params={
                "accountId": "account_456",
                "from": "2024-01-01",
                "to": "2024-01-31"
            },
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert len(transactions) == 1
        assert transactions[0]["amount"] == -150.00
        assert transactions[0]["category"] == "Food & Dining"

    @pytest.mark.django_db
    @patch('requests.delete')
    def test_delete_item(self, mock_delete, pluggy_client):
        """Should delete an item connection"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        pluggy_client.delete_item("item_123")

        mock_delete.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/items/item_123",
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @pytest.mark.django_db
    @patch('requests.get')
    def test_handle_api_error_response(self, mock_get, pluggy_client):
        """Should raise PluggyError on API error responses"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Invalid request",
            "code": "INVALID_REQUEST"
        }
        mock_get.return_value = mock_response

        with pytest.raises(PluggyError) as exc_info:
            pluggy_client.get_accounts("invalid_item")

        assert "Invalid request" in str(exc_info.value)

    @pytest.mark.django_db
    def test_requires_authentication(self, pluggy_client):
        """Should raise error when API key is not set"""
        # API key not set
        pluggy_client.api_key = None

        with pytest.raises(PluggyError) as exc_info:
            pluggy_client.get_connectors()

        assert "Authentication required" in str(exc_info.value)

    @pytest.mark.django_db
    @patch('requests.get')
    def test_get_categories(self, mock_get, pluggy_client):
        """Should retrieve available transaction categories"""
        pluggy_client.api_key = "test_api_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "cat_1",
                    "description": "Food & Dining",
                    "parentId": None,
                    "parentDescription": None
                },
                {
                    "id": "cat_2", 
                    "description": "Restaurants",
                    "parentId": "cat_1",
                    "parentDescription": "Food & Dining"
                }
            ]
        }
        mock_get.return_value = mock_response

        categories = pluggy_client.get_categories()

        mock_get.assert_called_once_with(
            "https://api.sandbox.pluggy.ai/categories",
            headers={
                "X-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )
        assert len(categories) == 2
        assert categories[1]["parentId"] == "cat_1"