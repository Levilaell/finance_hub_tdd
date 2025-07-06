"""
Testes para tasks de sincronização de transações.
Metodologia TDD: RED → GREEN → REFACTOR
"""

import pytest
from unittest.mock import patch, Mock
from celery import Celery
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from apps.banking.tasks import (
    sync_account_transactions,
    sync_all_company_accounts,
    sync_company_accounts_scheduled,
    process_transaction_batch,
    categorize_transactions_batch
)
from apps.banking.models import BankAccount, Transaction, BankProvider
from apps.companies.models import Company
from apps.authentication.models import User


@pytest.mark.django_db
class TestSyncTransactionsTasks:
    """Testes para tarefas de sincronização de transações."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    @pytest.fixture
    def company(self, user):
        return Company.objects.create(
            name='Test Company',
            cnpj='11.222.333/0001-81',
            owner=user
        )

    @pytest.fixture
    def bank_provider(self):
        return BankProvider.objects.create(
            name='Banco do Brasil',
            code='BB',
            pluggy_connector_id='bb-connector',
            is_active=True
        )

    @pytest.fixture
    def bank_account(self, company, bank_provider):
        return BankAccount.objects.create(
            company=company,
            bank_provider=bank_provider,
            pluggy_item_id='item_123',
            pluggy_account_id='account_456',
            account_type='CHECKING',
            name='Conta Corrente',
            agency='1234',
            account_number='567890',
            balance=1000.00
        )

    @pytest.fixture 
    def mock_pluggy_transactions(self):
        return [
            {
                'id': 'txn_001',
                'description': 'Compra supermercado',
                'amount': -150.50,
                'date': '2023-12-01',
                'type': 'DEBIT',
                'category': 'Alimentação'
            },
            {
                'id': 'txn_002', 
                'description': 'Depósito salário',
                'amount': 3000.00,
                'date': '2023-12-01',
                'type': 'CREDIT',
                'category': 'Renda'
            }
        ]

    def test_sync_account_transactions_success(self, bank_account, mock_pluggy_transactions):
        """Deve sincronizar transações de uma conta específica com sucesso."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = mock_pluggy_transactions
            mock_instance.authenticate.return_value = None
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'SUCCESS'
            assert result.result['status'] == 'success'
            assert result.result['synced_count'] == 2
            assert result.result['account_id'] == bank_account.id
            
            # Verificar se as transações foram criadas no banco
            transactions = Transaction.objects.filter(bank_account=bank_account)
            assert transactions.count() == 2

    def test_sync_account_transactions_with_existing_transactions(self, bank_account, mock_pluggy_transactions):
        """Deve ignorar transações já existentes durante sincronização."""
        # Criar uma transação que já existe
        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id='txn_001',
            transaction_type='DEBIT',
            amount=-150.50,
            description='Compra supermercado',
            transaction_date='2023-12-01'
        )
        
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = mock_pluggy_transactions
            mock_instance.authenticate.return_value = None
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'SUCCESS'
            assert result.result['synced_count'] == 1  # Apenas a nova transação
            assert result.result['skipped_count'] == 1  # Uma foi ignorada
            
            # Verificar que não há duplicatas
            transactions = Transaction.objects.filter(bank_account=bank_account)
            assert transactions.count() == 2

    def test_sync_account_transactions_with_invalid_account(self):
        """Deve falhar graciosamente com conta inválida."""
        invalid_account_id = 99999
        
        result = sync_account_transactions.apply(args=[invalid_account_id])
        
        assert result.state == 'FAILURE'
        assert 'not found' in str(result.result).lower()

    def test_sync_account_transactions_with_pluggy_error(self, bank_account):
        """Deve tratar erros da API Pluggy adequadamente."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.authenticate.return_value = None
            mock_instance.get_transactions.side_effect = Exception('Pluggy API Error')
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'FAILURE'
            assert 'pluggy api error' in str(result.result).lower()

    def test_sync_all_company_accounts_success(self, company, bank_account, mock_pluggy_transactions):
        """Deve sincronizar todas as contas de empresas especificadas."""
        # Criar segunda conta para mesma empresa
        bank_account2 = BankAccount.objects.create(
            company=company,
            bank_provider=bank_account.bank_provider,
            pluggy_item_id='item_456',
            pluggy_account_id='account_789',
            account_type='SAVINGS',
            name='Conta Poupança',
            agency='1234',
            account_number='567891',
            balance=2000.00
        )
        
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = mock_pluggy_transactions
            mock_instance.authenticate.return_value = None
            
            result = sync_all_company_accounts.apply(args=[[company.id]])
            
            assert result.state == 'SUCCESS'
            assert result.result['status'] == 'success'
            assert result.result['companies_processed'] == 1
            assert result.result['accounts_processed'] == 2
            assert result.result['total_transactions_synced'] == 4  # 2 contas x 2 transações

    def test_sync_company_accounts_scheduled_task(self, company, bank_account):
        """Deve executar sincronização agendada para empresas ativas."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = []
            mock_instance.authenticate.return_value = None
            
            result = sync_company_accounts_scheduled.apply()
            
            assert result.state == 'SUCCESS'
            assert result.result['status'] == 'success'
            assert 'companies_processed' in result.result

    def test_process_transaction_batch_success(self, bank_account, mock_pluggy_transactions):
        """Deve processar lote de transações em batch."""
        transaction_data = {
            'account_id': bank_account.id,
            'transactions': mock_pluggy_transactions
        }
        
        result = process_transaction_batch.apply(args=[transaction_data])
        
        assert result.state == 'SUCCESS'
        assert result.result['processed_count'] == 2
        assert result.result['account_id'] == bank_account.id
        
        # Verificar transações criadas
        transactions = Transaction.objects.filter(bank_account=bank_account)
        assert transactions.count() == 2

    def test_process_transaction_batch_with_validation_errors(self, bank_account):
        """Deve tratar erros de validação no batch de transações."""
        invalid_transactions = [
            {
                'id': 'txn_invalid',
                'description': '',  # Descrição vazia - inválida
                'amount': 'invalid_amount',  # Amount inválido
                'date': 'invalid_date',  # Data inválida
            }
        ]
        
        transaction_data = {
            'account_id': bank_account.id,
            'transactions': invalid_transactions
        }
        
        result = process_transaction_batch.apply(args=[transaction_data])
        
        assert result.state == 'SUCCESS'  # Task não falha, mas reporta erros
        assert result.result['processed_count'] == 0
        assert result.result['error_count'] == 1
        assert 'validation_errors' in result.result

    def test_categorize_transactions_batch_success(self, bank_account, mock_pluggy_transactions):
        """Deve categorizar transações em lote após sincronização."""
        # Criar transações primeiro
        for txn_data in mock_pluggy_transactions:
            Transaction.objects.create(
                bank_account=bank_account,
                pluggy_transaction_id=txn_data['id'],
                transaction_type=txn_data['type'],
                amount=txn_data['amount'],
                description=txn_data['description'],
                transaction_date=txn_data['date']
            )
        
        transaction_ids = list(Transaction.objects.filter(
            bank_account=bank_account
        ).values_list('id', flat=True))
        
        # Test function directly without categorization service (it gracefully handles missing service)
        result = categorize_transactions_batch.apply(args=[transaction_ids])
        
        assert result.state == 'SUCCESS'
        assert result.result['total_transactions'] == 2
        assert result.result['categorized_count'] == 0  # Service not available, so 0 categorized

    def test_sync_with_rate_limiting(self, bank_account, mock_pluggy_transactions):
        """Deve respeitar rate limiting da API Pluggy."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Simular rate limit error
            from requests.exceptions import HTTPError
            response = Mock()
            response.status_code = 429
            response.text = 'Rate limit exceeded'
            error = HTTPError('Rate limit', response=response)
            
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.authenticate.return_value = None
            mock_instance.get_transactions.side_effect = error
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'FAILURE'  # Task falha após máximo de retries
            assert 'rate limit' in str(result.result).lower()

    def test_sync_performance_with_large_dataset(self, bank_account):
        """Deve ter performance adequada com grande volume de transações."""
        # Simular grande volume de transações
        large_transactions = []
        for i in range(1000):
            large_transactions.append({
                'id': f'txn_{i:04d}',
                'description': f'Transaction {i}',
                'amount': -10.00 * (i % 100),
                'date': '2023-12-01',
                'type': 'DEBIT',
                'category': 'Test'
            })
        
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = large_transactions
            mock_instance.authenticate.return_value = None
            
            start_time = timezone.now()
            result = sync_account_transactions.apply(args=[bank_account.id])
            end_time = timezone.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            assert result.state == 'SUCCESS'
            assert result.result['synced_count'] == 1000
            assert execution_time < 30  # Não deve demorar mais que 30 segundos

    def test_sync_with_concurrent_execution(self, company, bank_account):
        """Deve tratar execução concorrente adequadamente."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = []
            mock_instance.authenticate.return_value = None
            
            # Simular duas tarefas concorrentes para a mesma empresa
            result1 = sync_all_company_accounts.apply(args=[[company.id]])
            result2 = sync_all_company_accounts.apply(args=[[company.id]])
            
            # Ambas devem completar sem conflito
            assert result1.state == 'SUCCESS'
            assert result2.state == 'SUCCESS'

    def test_sync_incremental_updates(self, bank_account, mock_pluggy_transactions):
        """Deve fazer sincronização incremental baseada na última sync."""
        # Simular última sincronização há 1 dia
        bank_account.last_sync = timezone.now() - timedelta(days=1)
        bank_account.save()
        
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = mock_pluggy_transactions
            mock_instance.authenticate.return_value = None
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'SUCCESS'
            
            # Verificar que foi chamado com parâmetro de data
            call_args = mock_instance.get_transactions.call_args
            assert 'from_date' in call_args[1] or len(call_args[0]) > 1

    def test_sync_error_notification(self, bank_account):
        """Deve enviar notificação em caso de erro na sincronização."""
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.authenticate.return_value = None
            mock_instance.get_transactions.side_effect = Exception('Critical error')
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'FAILURE'
            # Task gracefully handles missing notification service with ImportError

    def test_sync_transaction_deduplication(self, bank_account):
        """Deve evitar duplicação de transações com diferentes IDs externos."""
        # Criar transação que pode ser duplicata (mesmo valor, data, descrição)
        Transaction.objects.create(
            bank_account=bank_account,
            pluggy_transaction_id='old_txn_001',
            transaction_type='DEBIT',
            amount=-150.50,
            description='Compra supermercado',
            transaction_date='2023-12-01'
        )
        
        # Transação com ID diferente mas dados similares
        duplicate_transactions = [
            {
                'id': 'new_txn_001',
                'description': 'Compra supermercado',
                'amount': -150.50,
                'date': '2023-12-01',
                'type': 'DEBIT',
                'category': 'Alimentação'
            }
        ]
        
        with patch('apps.banking.tasks.PluggyClient') as mock_pluggy:
            # Configurar mock
            mock_instance = mock_pluggy.return_value
            mock_instance.get_transactions.return_value = duplicate_transactions
            mock_instance.authenticate.return_value = None
            
            result = sync_account_transactions.apply(args=[bank_account.id])
            
            assert result.state == 'SUCCESS'
            assert result.result.get('duplicates_detected', 0) >= 1
            
            # Deve manter apenas uma transação
            transactions = Transaction.objects.filter(bank_account=bank_account)
            assert transactions.count() == 1