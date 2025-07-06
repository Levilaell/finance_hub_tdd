"""
Testes para RuleEngine de categorização.
Metodologia TDD: RED → GREEN → REFACTOR
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from django.test import TestCase
from apps.categories.services.rules import RuleEngine, RuleCondition, RuleOperator
from apps.categories.models import Category, CategorizationRule
from apps.companies.models import Company
from apps.authentication.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def company(user):
    return Company.objects.create(
        name='Test Company',
        cnpj='11.222.333/0001-81',
        owner=user
    )


@pytest.fixture
def category(company):
    return Category.objects.create(
        company=company,
        name='Test Category',
        color='#FF0000'
    )


@pytest.mark.django_db
class TestRuleEngine:
    """Testes para o motor de regras de categorização."""

    def test_rule_engine_initialization(self):
        """Deve inicializar RuleEngine corretamente."""
        engine = RuleEngine()
        
        assert engine is not None
        assert hasattr(engine, 'evaluate')
        assert hasattr(engine, 'compile_rule')

    def test_evaluate_contains_condition_true(self):
        """Deve avaliar condição CONTAINS como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='supermercado'
        )
        
        transaction_data = {
            'description': 'Compra no supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_contains_condition_false(self):
        """Deve avaliar condição CONTAINS como falsa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='farmacia'
        )
        
        transaction_data = {
            'description': 'Compra no supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_equals_condition_true(self):
        """Deve avaliar condição EQUALS como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='transaction_type',
            operator=RuleOperator.EQUALS,
            field_value='DEBIT'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_equals_condition_false(self):
        """Deve avaliar condição EQUALS como falsa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='transaction_type',
            operator=RuleOperator.EQUALS,
            field_value='CREDIT'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_greater_than_condition_true(self):
        """Deve avaliar condição GREATER_THAN como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='amount',
            operator=RuleOperator.GREATER_THAN,
            field_value='100.00'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('150.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_greater_than_condition_false(self):
        """Deve avaliar condição GREATER_THAN como falsa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='amount',
            operator=RuleOperator.GREATER_THAN,
            field_value='200.00'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('150.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_less_than_condition_true(self):
        """Deve avaliar condição LESS_THAN como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='amount',
            operator=RuleOperator.LESS_THAN,
            field_value='200.00'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('150.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_less_than_condition_false(self):
        """Deve avaliar condição LESS_THAN como falsa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='amount',
            operator=RuleOperator.LESS_THAN,
            field_value='100.00'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('150.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_starts_with_condition_true(self):
        """Deve avaliar condição STARTS_WITH como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.STARTS_WITH,
            field_value='Compra'
        )
        
        transaction_data = {
            'description': 'Compra no supermercado',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_ends_with_condition_true(self):
        """Deve avaliar condição ENDS_WITH como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.ENDS_WITH,
            field_value='ABC'
        )
        
        transaction_data = {
            'description': 'Supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_regex_condition_true(self):
        """Deve avaliar condição REGEX como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.REGEX,
            field_value=r'^\d{2}/\d{2}/\d{4}'  # Data no formato dd/mm/yyyy
        )
        
        transaction_data = {
            'description': '01/12/2023 Compra',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_regex_condition_false(self):
        """Deve avaliar condição REGEX como falsa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.REGEX,
            field_value=r'^\d{2}/\d{2}/\d{4}'  # Data no formato dd/mm/yyyy
        )
        
        transaction_data = {
            'description': 'Compra sem data',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_in_list_condition_true(self):
        """Deve avaliar condição IN_LIST como verdadeira."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='transaction_type',
            operator=RuleOperator.IN_LIST,
            field_value='DEBIT,CREDIT'  # Lista separada por vírgula
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_case_insensitive_contains(self):
        """Deve avaliar condições de texto sem distinção de maiúsculas."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='SUPERMERCADO'
        )
        
        transaction_data = {
            'description': 'compra no supermercado abc',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_evaluate_with_missing_field(self):
        """Deve tratar campo ausente graciosamente."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='nonexistent_field',
            operator=RuleOperator.CONTAINS,
            field_value='test'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_compile_rule_from_categorization_rule(self, company, category):
        """Deve compilar RuleCondition a partir de CategorizationRule."""
        engine = RuleEngine()
        
        categorization_rule = CategorizationRule.objects.create(
            company=company,
            name='Test Rule',
            category=category,
            condition_type='CONTAINS',
            field_name='description',
            field_value='supermercado',
            priority=10
        )
        
        condition = engine.compile_rule(categorization_rule)
        
        assert isinstance(condition, RuleCondition)
        assert condition.field_name == 'description'
        assert condition.operator == RuleOperator.CONTAINS
        assert condition.field_value == 'supermercado'

    def test_compile_rule_with_invalid_operator(self, company, category):
        """Deve tratar operador inválido ao compilar regra."""
        engine = RuleEngine()
        
        categorization_rule = CategorizationRule.objects.create(
            company=company,
            name='Invalid Rule',
            category=category,
            condition_type='INVALID_OPERATOR',
            field_name='description',
            field_value='test',
            priority=10
        )
        
        with pytest.raises(ValueError):
            engine.compile_rule(categorization_rule)

    def test_evaluate_multiple_conditions_and(self):
        """Deve avaliar múltiplas condições com operador AND."""
        engine = RuleEngine()
        
        conditions = [
            RuleCondition(
                field_name='description',
                operator=RuleOperator.CONTAINS,
                field_value='supermercado'
            ),
            RuleCondition(
                field_name='amount',
                operator=RuleOperator.GREATER_THAN,
                field_value='30.00'
            )
        ]
        
        transaction_data = {
            'description': 'Compra supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate_multiple(conditions, transaction_data, operator='AND')
        
        assert result is True

    def test_evaluate_multiple_conditions_and_false(self):
        """Deve avaliar múltiplas condições com operador AND como falso."""
        engine = RuleEngine()
        
        conditions = [
            RuleCondition(
                field_name='description',
                operator=RuleOperator.CONTAINS,
                field_value='supermercado'
            ),
            RuleCondition(
                field_name='amount',
                operator=RuleOperator.GREATER_THAN,
                field_value='100.00'  # Falso
            )
        ]
        
        transaction_data = {
            'description': 'Compra supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate_multiple(conditions, transaction_data, operator='AND')
        
        assert result is False

    def test_evaluate_multiple_conditions_or(self):
        """Deve avaliar múltiplas condições com operador OR."""
        engine = RuleEngine()
        
        conditions = [
            RuleCondition(
                field_name='description',
                operator=RuleOperator.CONTAINS,
                field_value='farmacia'  # Falso
            ),
            RuleCondition(
                field_name='amount',
                operator=RuleOperator.GREATER_THAN,
                field_value='30.00'  # Verdadeiro
            )
        ]
        
        transaction_data = {
            'description': 'Compra supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate_multiple(conditions, transaction_data, operator='OR')
        
        assert result is True

    def test_evaluate_multiple_conditions_or_false(self):
        """Deve avaliar múltiplas condições com operador OR como falso."""
        engine = RuleEngine()
        
        conditions = [
            RuleCondition(
                field_name='description',
                operator=RuleOperator.CONTAINS,
                field_value='farmacia'  # Falso
            ),
            RuleCondition(
                field_name='amount',
                operator=RuleOperator.GREATER_THAN,
                field_value='100.00'  # Falso
            )
        ]
        
        transaction_data = {
            'description': 'Compra supermercado ABC',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate_multiple(conditions, transaction_data, operator='OR')
        
        assert result is False

    def test_performance_with_complex_regex(self):
        """Deve ter performance adequada com regex complexa."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.REGEX,
            field_value=r'(?i)^(pix|ted|doc|transferencia).*(?:banco|btg|itau|bradesco)'
        )
        
        transaction_data = {
            'description': 'PIX transferencia banco do brasil',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        import time
        start_time = time.time()
        result = engine.evaluate(condition, transaction_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result is True
        assert execution_time < 0.001  # Menos de 1ms

    def test_evaluate_with_null_values(self):
        """Deve tratar valores nulos adequadamente."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='test'
        )
        
        transaction_data = {
            'description': None,
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_with_empty_string(self):
        """Deve tratar strings vazias adequadamente."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='test'
        )
        
        transaction_data = {
            'description': '',
            'amount': Decimal('50.00'),
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is False

    def test_evaluate_amount_with_string_value(self):
        """Deve converter strings para Decimal ao avaliar valores monetários."""
        engine = RuleEngine()
        
        condition = RuleCondition(
            field_name='amount',
            operator=RuleOperator.GREATER_THAN,
            field_value='100.00'
        )
        
        transaction_data = {
            'description': 'Teste',
            'amount': '150.50',  # String ao invés de Decimal
            'transaction_type': 'DEBIT'
        }
        
        result = engine.evaluate(condition, transaction_data)
        
        assert result is True

    def test_rule_condition_class(self):
        """Deve criar RuleCondition corretamente."""
        condition = RuleCondition(
            field_name='description',
            operator=RuleOperator.CONTAINS,
            field_value='supermercado'
        )
        
        assert condition.field_name == 'description'
        assert condition.operator == RuleOperator.CONTAINS
        assert condition.field_value == 'supermercado'

    def test_rule_operator_enum(self):
        """Deve ter todos os operadores necessários definidos."""
        operators = [
            RuleOperator.EQUALS,
            RuleOperator.CONTAINS,
            RuleOperator.STARTS_WITH,
            RuleOperator.ENDS_WITH,
            RuleOperator.GREATER_THAN,
            RuleOperator.LESS_THAN,
            RuleOperator.REGEX,
            RuleOperator.IN_LIST
        ]
        
        for operator in operators:
            assert operator is not None
            assert isinstance(operator.value, str)

    def test_caching_compiled_rules(self, company, category):
        """Deve fazer cache de regras compiladas para performance."""
        engine = RuleEngine()
        
        categorization_rule = CategorizationRule.objects.create(
            company=company,
            name='Cache Test Rule',
            category=category,
            condition_type='CONTAINS',
            field_name='description',
            field_value='supermercado',
            priority=10
        )
        
        # Primeira compilação
        condition1 = engine.compile_rule(categorization_rule)
        
        # Segunda compilação (deveria usar cache)
        condition2 = engine.compile_rule(categorization_rule)
        
        # Deve ser a mesma instância se cache for implementado
        assert condition1.field_name == condition2.field_name
        assert condition1.operator == condition2.operator
        assert condition1.field_value == condition2.field_value