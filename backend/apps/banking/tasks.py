from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import uuid
import logging
from typing import List, Dict, Any

from .models import BankAccount, Transaction, BankProvider
from .services.pluggy import PluggyClient
from apps.companies.models import Company

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_account_transactions(self, account_id: int) -> Dict[str, Any]:
    """
    Sync transactions for a specific bank account.
    
    Args:
        account_id: ID da conta bancária para sincronizar
        
    Returns:
        Dict com resultado da sincronização
    """
    try:
        # Buscar conta bancária
        try:
            bank_account = BankAccount.objects.get(id=account_id, is_active=True)
        except BankAccount.DoesNotExist:
            raise Exception(f"Bank account {account_id} not found")
        
        # Inicializar cliente Pluggy
        from django.conf import settings
        
        client_id = getattr(settings, 'PLUGGY_CLIENT_ID', 'test_client_id')
        client_secret = getattr(settings, 'PLUGGY_CLIENT_SECRET', 'test_client_secret')
        pluggy_client = PluggyClient(client_id, client_secret)
        
        # Autenticar cliente
        pluggy_client.authenticate()
        
        # Determinar data de início para sincronização incremental
        from_date = None
        if bank_account.last_sync:
            from_date = bank_account.last_sync.strftime('%Y-%m-%d')
        
        # Buscar transações do Pluggy
        try:
            if from_date:
                transactions_data = pluggy_client.get_transactions(
                    bank_account.pluggy_account_id, 
                    from_date=from_date
                )
            else:
                transactions_data = pluggy_client.get_transactions(
                    bank_account.pluggy_account_id
                )
        except Exception as e:
            if '429' in str(e) or 'rate limit' in str(e).lower():
                # Rate limit - agendar retry
                try:
                    raise self.retry(countdown=600, exc=e)
                except self.MaxRetriesExceededError:
                    raise Exception(f"Rate limit exceeded after max retries: {str(e)}")
            raise Exception(f"Pluggy API Error: {str(e)}")
        
        # Processar transações
        synced_count = 0
        skipped_count = 0
        duplicates_detected = 0
        
        with transaction.atomic():
            for txn_data in transactions_data:
                # Verificar se transação já existe por ID
                existing = Transaction.objects.filter(
                    bank_account=bank_account,
                    pluggy_transaction_id=txn_data['id']
                ).exists()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Verificar duplicata por dados similares (mesmo valor, data, descrição)
                potential_duplicate = Transaction.objects.filter(
                    bank_account=bank_account,
                    amount=float(txn_data['amount']),
                    description=txn_data['description'],
                    transaction_date=txn_data['date']
                ).exists()
                
                if potential_duplicate:
                    duplicates_detected += 1
                    skipped_count += 1
                    continue
                
                # Criar nova transação
                Transaction.objects.create(
                    bank_account=bank_account,
                    pluggy_transaction_id=txn_data['id'],
                    transaction_type=txn_data['type'],
                    amount=float(txn_data['amount']),
                    description=txn_data['description'],
                    transaction_date=txn_data['date'],
                    category=txn_data.get('category', ''),
                    subcategory=txn_data.get('subcategory', ''),
                    is_pending=txn_data.get('is_pending', False)
                )
                synced_count += 1
            
            # Atualizar timestamp de última sincronização
            bank_account.last_sync = timezone.now()
            bank_account.save()
        
        return {
            "status": "success",
            "account_id": account_id,
            "synced_count": synced_count,
            "skipped_count": skipped_count,
            "duplicates_detected": duplicates_detected
        }
        
    except Exception as e:
        logger.error(f"Error syncing account {account_id}: {str(e)}")
        
        # Enviar notificação de erro se disponível
        try:
            from apps.notifications.services.notifications import NotificationService
            notification_service = NotificationService()
            notification_service.send_error_notification(
                f"Sync failed for account {account_id}",
                str(e)
            )
        except ImportError:
            pass  # Serviço de notificações não implementado ainda
        
        raise


@shared_task
def sync_all_company_accounts(company_ids: List[int]) -> Dict[str, Any]:
    """
    Sync transactions for all accounts of specified companies.
    
    Args:
        company_ids: Lista de IDs das empresas
        
    Returns:
        Dict com resultado da sincronização
    """
    try:
        companies_processed = 0
        accounts_processed = 0
        total_transactions_synced = 0
        
        for company_id in company_ids:
            try:
                company = Company.objects.get(id=company_id)
                bank_accounts = BankAccount.objects.filter(
                    company=company,
                    is_active=True
                )
                
                for account in bank_accounts:
                    result = sync_account_transactions.apply(args=[account.id])
                    if result.state == 'SUCCESS':
                        accounts_processed += 1
                        total_transactions_synced += result.result.get('synced_count', 0)
                
                companies_processed += 1
                
            except Company.DoesNotExist:
                logger.warning(f"Company {company_id} not found")
                continue
        
        return {
            "status": "success",
            "companies_processed": companies_processed,
            "accounts_processed": accounts_processed,
            "total_transactions_synced": total_transactions_synced
        }
        
    except Exception as e:
        logger.error(f"Error syncing companies {company_ids}: {str(e)}")
        raise


@shared_task
def sync_company_accounts_scheduled() -> Dict[str, Any]:
    """
    Tarefa agendada para sincronizar contas de todas as empresas ativas.
    
    Returns:
        Dict com resultado da sincronização agendada
    """
    try:
        # Buscar todas as empresas ativas
        active_companies = Company.objects.filter(is_active=True)
        company_ids = list(active_companies.values_list('id', flat=True))
        
        if not company_ids:
            return {
                "status": "success",
                "companies_processed": 0,
                "message": "No active companies found"
            }
        
        # Executar sincronização
        result = sync_all_company_accounts.apply(args=[company_ids])
        
        return {
            "status": "success",
            "companies_processed": len(company_ids),
            "sync_result": result.result
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled sync: {str(e)}")
        raise


@shared_task
def process_transaction_batch(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa lote de transações em batch para performance.
    
    Args:
        transaction_data: Dict com account_id e lista de transactions
        
    Returns:
        Dict com resultado do processamento
    """
    try:
        account_id = transaction_data['account_id']
        transactions = transaction_data['transactions']
        
        try:
            bank_account = BankAccount.objects.get(id=account_id)
        except BankAccount.DoesNotExist:
            raise Exception(f"Bank account {account_id} not found")
        
        processed_count = 0
        error_count = 0
        validation_errors = []
        
        with transaction.atomic():
            for txn_data in transactions:
                try:
                    # Validar dados da transação
                    if not txn_data.get('description'):
                        raise ValueError("Description is required")
                    
                    if not isinstance(txn_data.get('amount'), (int, float)):
                        raise ValueError("Invalid amount")
                    
                    # Validar data
                    try:
                        datetime.strptime(txn_data['date'], '%Y-%m-%d')
                    except (ValueError, KeyError):
                        raise ValueError("Invalid date format")
                    
                    # Criar transação
                    Transaction.objects.create(
                        bank_account=bank_account,
                        pluggy_transaction_id=txn_data['id'],
                        transaction_type=txn_data.get('type', 'DEBIT'),
                        amount=float(txn_data['amount']),
                        description=txn_data['description'],
                        transaction_date=txn_data['date'],
                        category=txn_data.get('category', ''),
                        subcategory=txn_data.get('subcategory', ''),
                        is_pending=txn_data.get('is_pending', False)
                    )
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    validation_errors.append({
                        'transaction_id': txn_data.get('id'),
                        'error': str(e)
                    })
        
        return {
            "status": "success",
            "account_id": account_id,
            "processed_count": processed_count,
            "error_count": error_count,
            "validation_errors": validation_errors
        }
        
    except Exception as e:
        logger.error(f"Error processing transaction batch: {str(e)}")
        raise


@shared_task
def categorize_transactions_batch(transaction_ids: List[int]) -> Dict[str, Any]:
    """
    Categoriza transações em lote após sincronização.
    
    Args:
        transaction_ids: Lista de IDs das transações
        
    Returns:
        Dict com resultado da categorização
    """
    try:
        categorized_count = 0
        total_transactions = len(transaction_ids)
        
        # Importar serviço de categorização se disponível
        try:
            from apps.categories.services.categorization import CategorizationService
            categorization_service = CategorizationService()
            
            transactions = Transaction.objects.filter(id__in=transaction_ids)
            
            for transaction_obj in transactions:
                try:
                    category = categorization_service.categorize_transaction(transaction_obj)
                    if category:
                        transaction_obj.category = category
                        transaction_obj.save()
                        categorized_count += 1
                except Exception as e:
                    logger.warning(f"Failed to categorize transaction {transaction_obj.id}: {str(e)}")
                    
        except ImportError:
            logger.info("Categorization service not available")
        
        return {
            "status": "success",
            "total_transactions": total_transactions,
            "categorized_count": categorized_count
        }
        
    except Exception as e:
        logger.error(f"Error categorizing transactions: {str(e)}")
        raise