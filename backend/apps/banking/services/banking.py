import os
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import logging

from .pluggy import PluggyClient, PluggyError
from ..models import BankProvider, BankAccount, Transaction

logger = logging.getLogger(__name__)


class BankingServiceError(Exception):
    """Custom exception for Banking Service errors"""
    pass


class BankingService:
    """Service for managing bank integrations via Pluggy"""

    def __init__(self):
        self.pluggy_client = PluggyClient(
            client_id=getattr(settings, 'PLUGGY_CLIENT_ID', os.getenv('PLUGGY_CLIENT_ID')),
            client_secret=getattr(settings, 'PLUGGY_CLIENT_SECRET', os.getenv('PLUGGY_CLIENT_SECRET')),
            sandbox=getattr(settings, 'PLUGGY_SANDBOX', True)
        )

    def _authenticate(self):
        """Ensure Pluggy client is authenticated"""
        if not self.pluggy_client.api_key:
            try:
                self.pluggy_client.authenticate()
            except PluggyError as e:
                raise BankingServiceError(f"Failed to authenticate with Pluggy: {str(e)}")

    def sync_bank_providers(self) -> Dict[str, int]:
        """Sync bank providers from Pluggy"""
        try:
            self._authenticate()
            connectors = self.pluggy_client.get_connectors()
            
            created_count = 0
            updated_count = 0
            
            for connector in connectors:
                # Generate code if not provided
                code = connector.get("code", connector["id"][:10])
                
                provider, created = BankProvider.objects.update_or_create(
                    pluggy_connector_id=connector["id"],
                    defaults={
                        "name": connector["name"],
                        "code": code,
                        "is_active": True,
                        "supports_checking_account": True,
                        "supports_savings_account": True,
                        "supports_credit_card": connector.get("type") == "CREDIT_CARD",
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            logger.info(f"Synced bank providers: {created_count} created, {updated_count} updated")
            return {"created": created_count, "updated": updated_count}
            
        except PluggyError as e:
            raise BankingServiceError(f"Failed to sync bank providers: {str(e)}")

    def connect_bank_account(self, company, bank_provider: BankProvider, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Connect a bank account via Pluggy"""
        try:
            self._authenticate()
            
            item = self.pluggy_client.create_item(
                bank_provider.pluggy_connector_id,
                credentials
            )
            
            logger.info(f"Connected bank account for company {company.id}, item {item['id']}")
            return {
                "item_id": item["id"],
                "status": item["status"],
                "execution_status": item.get("executionStatus"),
                "created_at": item.get("createdAt")
            }
            
        except PluggyError as e:
            raise BankingServiceError(f"Failed to connect bank account: {str(e)}")

    def sync_bank_accounts(self, company, bank_provider: BankProvider, item_id: str) -> Dict[str, int]:
        """Sync bank accounts from Pluggy item"""
        try:
            self._authenticate()
            
            accounts = self.pluggy_client.get_accounts(item_id)
            
            created_count = 0
            updated_count = 0
            
            for account_data in accounts:
                account, created = BankAccount.objects.update_or_create(
                    company=company,
                    pluggy_account_id=account_data["id"],
                    defaults={
                        "bank_provider": bank_provider,
                        "pluggy_item_id": item_id,
                        "account_type": self._map_account_type(account_data["type"]),
                        "name": account_data.get("name", ""),
                        "agency": "",  # Pluggy doesn't provide agency info
                        "account_number": account_data.get("number", ""),
                        "balance": Decimal(str(account_data.get("balance", 0))),
                        "is_active": True,
                        "last_sync": timezone.now(),
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            logger.info(f"Synced bank accounts: {created_count} created, {updated_count} updated")
            return {"created": created_count, "updated": updated_count}
            
        except PluggyError as e:
            raise BankingServiceError(f"Failed to sync bank accounts: {str(e)}")

    def sync_transactions(self, bank_account: BankAccount, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, int]:
        """Sync transactions from Pluggy account"""
        try:
            self._authenticate()
            
            transactions = self.pluggy_client.get_transactions(
                bank_account.pluggy_account_id,
                from_date=from_date,
                to_date=to_date
            )
            
            created_count = 0
            updated_count = 0
            
            for trans_data in transactions:
                amount = abs(Decimal(str(trans_data["amount"])))
                transaction_type = self._determine_transaction_type(trans_data["amount"])
                
                # Parse transaction date
                trans_date = datetime.strptime(trans_data["date"], "%Y-%m-%d").date()
                
                transaction, created = Transaction.objects.update_or_create(
                    bank_account=bank_account,
                    pluggy_transaction_id=trans_data["id"],
                    defaults={
                        "transaction_type": transaction_type,
                        "amount": amount,
                        "description": trans_data.get("description", ""),
                        "transaction_date": trans_date,
                        "category": trans_data.get("category", ""),
                        "subcategory": "",
                        "is_pending": False,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            # Update account last sync
            bank_account.last_sync = timezone.now()
            bank_account.save(update_fields=["last_sync"])
            
            logger.info(f"Synced transactions: {created_count} created, {updated_count} updated")
            return {"created": created_count, "updated": updated_count}
            
        except PluggyError as e:
            raise BankingServiceError(f"Failed to sync transactions: {str(e)}")

    def get_connection_status(self, item_id: str) -> Dict[str, Any]:
        """Get connection status from Pluggy"""
        try:
            self._authenticate()
            return self.pluggy_client.get_item_status(item_id)
        except PluggyError as e:
            raise BankingServiceError(f"Failed to get connection status: {str(e)}")

    def disconnect_bank_account(self, bank_account: BankAccount) -> None:
        """Disconnect bank account and delete from Pluggy"""
        try:
            self._authenticate()
            
            # Delete from Pluggy
            self.pluggy_client.delete_item(bank_account.pluggy_item_id)
            
            # Deactivate account (preserve transaction history)
            bank_account.is_active = False
            bank_account.save(update_fields=["is_active"])
            
            logger.info(f"Disconnected bank account {bank_account.id}")
            
        except PluggyError as e:
            raise BankingServiceError(f"Failed to disconnect bank account: {str(e)}")

    def _determine_transaction_type(self, amount: float) -> str:
        """Determine transaction type from amount"""
        return "CREDIT" if amount > 0 else "DEBIT"

    def _map_account_type(self, pluggy_type: str) -> str:
        """Map Pluggy account type to internal type"""
        type_mapping = {
            "CHECKING": "CHECKING",
            "SAVINGS": "SAVINGS", 
            "CREDIT_CARD": "CREDIT_CARD",
        }
        return type_mapping.get(pluggy_type, "CHECKING")  # Default to checking