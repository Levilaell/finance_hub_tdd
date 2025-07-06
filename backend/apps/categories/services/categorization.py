"""
Serviço de categorização automática de transações.
Usa o RuleEngine para aplicar regras de categorização.
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
from django.db.models import QuerySet

from ..models import Category, CategorizationRule
from .rules import RuleEngine, RuleCondition


class CategorizationService:
    """Serviço para categorização automática de transações."""
    
    def __init__(self, company):
        """
        Inicializa o serviço de categorização.
        
        Args:
            company: Instância da empresa
        """
        self.company = company
        self.rule_engine = RuleEngine()
    
    def get_active_rules(self) -> QuerySet:
        """
        Obtém regras ativas da empresa ordenadas por prioridade.
        
        Returns:
            QuerySet de CategorizationRule ordenadas por prioridade (desc)
        """
        return CategorizationRule.objects.filter(
            company=self.company,
            is_active=True
        ).order_by('-priority')
    
    def categorize_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Category]:
        """
        Categoriza uma transação usando as regras ativas.
        
        Args:
            transaction_data: Dados da transação
            
        Returns:
            Categoria encontrada ou categoria padrão
        """
        if not self.validate_transaction_data(transaction_data):
            return self.get_default_category()
        
        # Buscar regras ativas ordenadas por prioridade
        active_rules = self.get_active_rules()
        
        # Aplicar regras em ordem de prioridade
        for rule in active_rules:
            if self.apply_rule_to_transaction(rule, transaction_data):
                return rule.category
        
        # Se nenhuma regra foi aplicada, usar categoria padrão
        return self.get_default_category()
    
    def categorize_transactions(self, transactions_data: List[Dict[str, Any]]) -> List[Category]:
        """
        Categoriza múltiplas transações em lote.
        
        Args:
            transactions_data: Lista de dados de transações
            
        Returns:
            Lista de categorias correspondentes
        """
        return [
            self.categorize_transaction(transaction_data)
            for transaction_data in transactions_data
        ]
    
    def apply_rule_to_transaction(self, rule: CategorizationRule, transaction_data: Dict[str, Any]) -> bool:
        """
        Aplica uma regra específica a uma transação.
        
        Args:
            rule: Regra de categorização
            transaction_data: Dados da transação
            
        Returns:
            True se a regra foi aplicada com sucesso
        """
        try:
            # Compilar regra para condição do motor
            condition = self.rule_engine.compile_rule(rule)
            
            # Avaliar condição
            return self.rule_engine.evaluate(condition, transaction_data)
        except Exception:
            # Em caso de erro na regra, não aplicar
            return False
    
    def get_default_category(self) -> Category:
        """
        Obtém ou cria a categoria padrão do sistema.
        
        Returns:
            Categoria padrão "Sem Categoria"
        """
        category, created = Category.objects.get_or_create(
            company=self.company,
            name='Sem Categoria',
            defaults={
                'color': '#9E9E9E',
                'is_system': True
            }
        )
        return category
    
    def validate_transaction_data(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Valida se os dados da transação estão no formato correto.
        
        Args:
            transaction_data: Dados da transação
            
        Returns:
            True se os dados são válidos
        """
        required_fields = ['description', 'amount', 'transaction_type']
        
        for field in required_fields:
            if field not in transaction_data:
                return False
                
        return True
    
    def get_categorization_stats(self, categorized_results: List[Category]) -> Dict[str, Any]:
        """
        Calcula estatísticas de categorização.
        
        Args:
            categorized_results: Lista de categorias resultado da categorização
            
        Returns:
            Dicionário com estatísticas
        """
        total_transactions = len(categorized_results)
        if total_transactions == 0:
            return {
                'total_transactions': 0,
                'categorized_transactions': 0,
                'uncategorized_transactions': 0,
                'categorization_rate': 0.0
            }
        
        # Obter categoria padrão para comparação
        default_category = self.get_default_category()
        
        # Contar transações categorizadas (não são da categoria padrão)
        categorized_count = sum(
            1 for category in categorized_results 
            if category.id != default_category.id
        )
        
        uncategorized_count = total_transactions - categorized_count
        categorization_rate = categorized_count / total_transactions
        
        return {
            'total_transactions': total_transactions,
            'categorized_transactions': categorized_count,
            'uncategorized_transactions': uncategorized_count,
            'categorization_rate': categorization_rate
        }