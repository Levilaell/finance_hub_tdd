"""
RuleEngine para categorização automática de transações.
Implementa sistema flexível de regras com múltiplos operadores.
"""

import re
from enum import Enum
from decimal import Decimal
from typing import Dict, Any, List, Union
from dataclasses import dataclass


class RuleOperator(Enum):
    """Operadores disponíveis para regras de categorização."""
    EQUALS = "EQUALS"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    REGEX = "REGEX"
    IN_LIST = "IN_LIST"


@dataclass
class RuleCondition:
    """Representa uma condição de regra compilada."""
    field_name: str
    operator: RuleOperator
    field_value: str


class RuleEngine:
    """Motor de regras para categorização automática de transações."""
    
    def __init__(self):
        """Inicializa o motor de regras."""
        self._compiled_rules_cache = {}
    
    def evaluate(self, condition: RuleCondition, transaction_data: Dict[str, Any]) -> bool:
        """
        Avalia uma condição contra dados de uma transação.
        
        Args:
            condition: Condição a ser avaliada
            transaction_data: Dados da transação
            
        Returns:
            True se a condição for atendida, False caso contrário
        """
        # Obter valor do campo
        field_value = transaction_data.get(condition.field_name)
        
        # Tratar valores nulos ou ausentes
        if field_value is None:
            return False
            
        # Converter para string se necessário para operações de texto
        if condition.operator in [
            RuleOperator.EQUALS, 
            RuleOperator.CONTAINS, 
            RuleOperator.STARTS_WITH,
            RuleOperator.ENDS_WITH, 
            RuleOperator.REGEX, 
            RuleOperator.IN_LIST
        ]:
            field_value = str(field_value)
            if not field_value:  # String vazia
                return False
        
        # Avaliar condição baseada no operador
        if condition.operator == RuleOperator.EQUALS:
            return self._evaluate_equals(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.CONTAINS:
            return self._evaluate_contains(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.STARTS_WITH:
            return self._evaluate_starts_with(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.ENDS_WITH:
            return self._evaluate_ends_with(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.GREATER_THAN:
            return self._evaluate_greater_than(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.LESS_THAN:
            return self._evaluate_less_than(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.REGEX:
            return self._evaluate_regex(field_value, condition.field_value)
            
        elif condition.operator == RuleOperator.IN_LIST:
            return self._evaluate_in_list(field_value, condition.field_value)
            
        else:
            raise ValueError(f"Operador não suportado: {condition.operator}")
    
    def _evaluate_equals(self, field_value: str, condition_value: str) -> bool:
        """Avalia igualdade exata (case insensitive para strings)."""
        return field_value.lower() == condition_value.lower()
    
    def _evaluate_contains(self, field_value: str, condition_value: str) -> bool:
        """Avalia se campo contém valor (case insensitive)."""
        return condition_value.lower() in field_value.lower()
    
    def _evaluate_starts_with(self, field_value: str, condition_value: str) -> bool:
        """Avalia se campo inicia com valor (case insensitive)."""
        return field_value.lower().startswith(condition_value.lower())
    
    def _evaluate_ends_with(self, field_value: str, condition_value: str) -> bool:
        """Avalia se campo termina com valor (case insensitive)."""
        return field_value.lower().endswith(condition_value.lower())
    
    def _evaluate_greater_than(self, field_value: Union[str, Decimal], condition_value: str) -> bool:
        """Avalia se valor numérico é maior que condição."""
        try:
            field_decimal = Decimal(str(field_value))
            condition_decimal = Decimal(condition_value)
            return field_decimal > condition_decimal
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_than(self, field_value: Union[str, Decimal], condition_value: str) -> bool:
        """Avalia se valor numérico é menor que condição."""
        try:
            field_decimal = Decimal(str(field_value))
            condition_decimal = Decimal(condition_value)
            return field_decimal < condition_decimal
        except (ValueError, TypeError):
            return False
    
    def _evaluate_regex(self, field_value: str, condition_value: str) -> bool:
        """Avalia expressão regular."""
        try:
            pattern = re.compile(condition_value, re.IGNORECASE)
            return bool(pattern.search(field_value))
        except re.error:
            return False
    
    def _evaluate_in_list(self, field_value: str, condition_value: str) -> bool:
        """Avalia se valor está na lista (separada por vírgula)."""
        values_list = [v.strip().lower() for v in condition_value.split(',')]
        return field_value.lower() in values_list
    
    def evaluate_multiple(self, conditions: List[RuleCondition], transaction_data: Dict[str, Any], operator: str = 'AND') -> bool:
        """
        Avalia múltiplas condições com operador lógico.
        
        Args:
            conditions: Lista de condições
            transaction_data: Dados da transação
            operator: 'AND' ou 'OR'
            
        Returns:
            Resultado da avaliação combinada
        """
        if not conditions:
            return True
            
        results = [self.evaluate(condition, transaction_data) for condition in conditions]
        
        if operator == 'AND':
            return all(results)
        elif operator == 'OR':
            return any(results)
        else:
            raise ValueError(f"Operador lógico não suportado: {operator}")
    
    def compile_rule(self, categorization_rule) -> RuleCondition:
        """
        Compila CategorizationRule em RuleCondition.
        
        Args:
            categorization_rule: Instância do modelo CategorizationRule
            
        Returns:
            RuleCondition compilada
            
        Raises:
            ValueError: Se operador for inválido
        """
        # Cache de regras compiladas para performance
        cache_key = f"{categorization_rule.id}_{categorization_rule.updated_at}"
        if cache_key in self._compiled_rules_cache:
            return self._compiled_rules_cache[cache_key]
        
        # Mapear string do banco para enum
        operator_mapping = {
            'EQUALS': RuleOperator.EQUALS,
            'CONTAINS': RuleOperator.CONTAINS,
            'STARTS_WITH': RuleOperator.STARTS_WITH,
            'ENDS_WITH': RuleOperator.ENDS_WITH,
            'GREATER_THAN': RuleOperator.GREATER_THAN,
            'LESS_THAN': RuleOperator.LESS_THAN,
            'REGEX': RuleOperator.REGEX,
            'IN_LIST': RuleOperator.IN_LIST,
        }
        
        operator = operator_mapping.get(categorization_rule.condition_type)
        if not operator:
            raise ValueError(f"Operador inválido: {categorization_rule.condition_type}")
        
        condition = RuleCondition(
            field_name=categorization_rule.field_name,
            operator=operator,
            field_value=categorization_rule.field_value
        )
        
        # Adicionar ao cache
        self._compiled_rules_cache[cache_key] = condition
        
        return condition