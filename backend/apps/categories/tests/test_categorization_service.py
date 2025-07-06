import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from django.test import TestCase
from apps.categories.models import Category, CategorizationRule
from apps.categories.services.categorization import CategorizationService
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
def categories(company):
    """Create test categories"""
    alimentacao = Category.objects.create(
        company=company,
        name="Alimentação",
        color="#FF5722",
    )
    
    transporte = Category.objects.create(
        company=company,
        name="Transporte",
        color="#2196F3",
    )
    
    sem_categoria = Category.objects.create(
        company=company,
        name="Sem Categoria",
        color="#9E9E9E",
        is_system=True,
    )
    
    return {
        "alimentacao": alimentacao,
        "transporte": transporte,
        "sem_categoria": sem_categoria,
    }


@pytest.fixture
def categorization_rules(company, categories):
    """Create test categorization rules"""
    # Rule for supermercado -> Alimentação
    rule1 = CategorizationRule.objects.create(
        company=company,
        name="Supermercado Rule",
        category=categories["alimentacao"],
        condition_type="CONTAINS",
        field_name="description",
        field_value="supermercado",
        priority=10,
    )
    
    # Rule for uber/taxi -> Transporte
    rule2 = CategorizationRule.objects.create(
        company=company,
        name="Uber Rule",
        category=categories["transporte"],
        condition_type="CONTAINS",
        field_name="description",
        field_value="uber",
        priority=8,
    )
    
    # Rule for high amounts -> should not match small transactions
    rule3 = CategorizationRule.objects.create(
        company=company,
        name="High Amount Rule",
        category=categories["transporte"],
        condition_type="GREATER_THAN",
        field_name="amount",
        field_value="1000.00",
        priority=5,
    )
    
    return {
        "supermercado": rule1,
        "uber": rule2,
        "high_amount": rule3,
    }


class TestCategorizationService:
    """Test suite for CategorizationService"""

    @pytest.mark.django_db
    def test_init_service_with_company(self, company):
        """Should initialize service with company"""
        service = CategorizationService(company)
        
        assert service.company == company

    @pytest.mark.django_db
    def test_get_active_rules_for_company(self, company, categorization_rules):
        """Should get only active rules for the company"""
        service = CategorizationService(company)
        
        rules = service.get_active_rules()
        
        assert rules.count() == 3
        assert all(rule.company == company for rule in rules)
        assert all(rule.is_active for rule in rules)

    @pytest.mark.django_db
    def test_get_active_rules_ordered_by_priority(self, company, categorization_rules):
        """Should get rules ordered by priority (descending)"""
        service = CategorizationService(company)
        
        rules = service.get_active_rules()
        priorities = [rule.priority for rule in rules]
        
        assert priorities == [10, 8, 5]  # Descending order

    @pytest.mark.django_db
    def test_categorize_transaction_with_matching_rule(self, company, categories, categorization_rules):
        """Should categorize transaction when rule matches"""
        service = CategorizationService(company)
        
        transaction_data = {
            "description": "Compra no supermercado",
            "amount": Decimal("50.00"),
            "transaction_type": "DEBIT"
        }
        
        category = service.categorize_transaction(transaction_data)
        
        assert category == categories["alimentacao"]

    @pytest.mark.django_db
    def test_categorize_transaction_with_multiple_matching_rules(self, company, categories):
        """Should use highest priority rule when multiple rules match"""
        # Create rules with different priorities
        rule_low = CategorizationRule.objects.create(
            company=company,
            name="Low Priority Rule",
            category=categories["transporte"],
            condition_type="CONTAINS",
            field_name="description",
            field_value="compra",
            priority=1,
        )
        
        rule_high = CategorizationRule.objects.create(
            company=company,
            name="High Priority Rule",
            category=categories["alimentacao"],
            condition_type="CONTAINS",
            field_name="description",
            field_value="compra",
            priority=10,
        )
        
        service = CategorizationService(company)
        
        transaction_data = {
            "description": "Compra no mercado",
            "amount": Decimal("30.00"),
            "transaction_type": "DEBIT"
        }
        
        category = service.categorize_transaction(transaction_data)
        
        # Should use high priority rule (alimentacao)
        assert category == categories["alimentacao"]

    @pytest.mark.django_db
    def test_categorize_transaction_no_matching_rules(self, company, categories, categorization_rules):
        """Should return default category when no rules match"""
        service = CategorizationService(company)
        
        transaction_data = {
            "description": "Transferência bancária",
            "amount": Decimal("100.00"),
            "transaction_type": "DEBIT"
        }
        
        category = service.categorize_transaction(transaction_data)
        
        assert category == categories["sem_categoria"]

    @pytest.mark.django_db
    def test_categorize_transaction_with_inactive_rules(self, company, categories):
        """Should ignore inactive rules"""
        # Create inactive rule
        CategorizationRule.objects.create(
            company=company,
            name="Inactive Rule",
            category=categories["alimentacao"],
            condition_type="CONTAINS",
            field_name="description",
            field_value="mercado",
            priority=10,
            is_active=False,  # Inactive
        )
        
        service = CategorizationService(company)
        
        transaction_data = {
            "description": "Compra no mercado",
            "amount": Decimal("50.00"),
            "transaction_type": "DEBIT"
        }
        
        category = service.categorize_transaction(transaction_data)
        
        # Should use default category since rule is inactive
        assert category.name == "Sem Categoria"

    @pytest.mark.django_db
    def test_categorize_transactions_batch(self, company, categories, categorization_rules):
        """Should categorize multiple transactions in batch"""
        service = CategorizationService(company)
        
        transactions_data = [
            {
                "description": "Supermercado ABC",
                "amount": Decimal("45.50"),
                "transaction_type": "DEBIT"
            },
            {
                "description": "Uber viagem",
                "amount": Decimal("15.00"),
                "transaction_type": "DEBIT"
            },
            {
                "description": "Transferência TED",
                "amount": Decimal("200.00"),
                "transaction_type": "DEBIT"
            }
        ]
        
        results = service.categorize_transactions(transactions_data)
        
        assert len(results) == 3
        assert results[0] == categories["alimentacao"]  # Supermercado
        assert results[1] == categories["transporte"]   # Uber
        assert results[2] == categories["sem_categoria"] # No match

    @pytest.mark.django_db
    def test_get_default_category(self, company, categories):
        """Should get default system category"""
        service = CategorizationService(company)
        
        default_category = service.get_default_category()
        
        assert default_category == categories["sem_categoria"]
        assert default_category.is_system is True

    @pytest.mark.django_db
    def test_get_default_category_creates_if_not_exists(self, company):
        """Should create default category if it doesn't exist"""
        service = CategorizationService(company)
        
        default_category = service.get_default_category()
        
        assert default_category is not None
        assert default_category.name == "Sem Categoria"
        assert default_category.is_system is True
        assert default_category.company == company

    @pytest.mark.django_db
    def test_apply_rule_to_transaction(self, company, categories, categorization_rules):
        """Should apply specific rule to transaction"""
        service = CategorizationService(company)
        rule = categorization_rules["supermercado"]
        
        transaction_data = {
            "description": "Compra supermercado XYZ",
            "amount": Decimal("35.00"),
            "transaction_type": "DEBIT"
        }
        
        matches = service.apply_rule_to_transaction(rule, transaction_data)
        
        assert matches is True

    @pytest.mark.django_db
    def test_apply_rule_to_transaction_no_match(self, company, categories, categorization_rules):
        """Should return False when rule doesn't match"""
        service = CategorizationService(company)
        rule = categorization_rules["supermercado"]
        
        transaction_data = {
            "description": "Compra na farmácia",
            "amount": Decimal("25.00"),
            "transaction_type": "DEBIT"
        }
        
        matches = service.apply_rule_to_transaction(rule, transaction_data)
        
        assert matches is False

    @pytest.mark.django_db
    def test_get_category_stats(self, company, categories, categorization_rules):
        """Should get categorization statistics"""
        service = CategorizationService(company)
        
        # Simulate some transactions
        transactions_data = [
            {"description": "Supermercado ABC", "amount": Decimal("45.50"), "transaction_type": "DEBIT"},
            {"description": "Supermercado DEF", "amount": Decimal("60.00"), "transaction_type": "DEBIT"},
            {"description": "Uber viagem", "amount": Decimal("15.00"), "transaction_type": "DEBIT"},
            {"description": "Transferência", "amount": Decimal("200.00"), "transaction_type": "DEBIT"},
        ]
        
        results = service.categorize_transactions(transactions_data)
        stats = service.get_categorization_stats(results)
        
        assert stats["total_transactions"] == 4
        assert stats["categorized_transactions"] == 3  # 2 alimentacao + 1 transporte
        assert stats["uncategorized_transactions"] == 1
        assert stats["categorization_rate"] == 0.75

    @pytest.mark.django_db
    def test_validate_transaction_data(self, company):
        """Should validate transaction data format"""
        service = CategorizationService(company)
        
        valid_data = {
            "description": "Test transaction",
            "amount": Decimal("50.00"),
            "transaction_type": "DEBIT"
        }
        
        invalid_data = {
            "description": "Test transaction",
            # Missing amount and transaction_type
        }
        
        assert service.validate_transaction_data(valid_data) is True
        assert service.validate_transaction_data(invalid_data) is False

    @pytest.mark.django_db
    def test_categorize_with_amount_based_rule(self, company, categories, categorization_rules):
        """Should categorize based on amount rules"""
        service = CategorizationService(company)
        
        # High amount transaction
        transaction_data = {
            "description": "Compra cara",
            "amount": Decimal("1500.00"),  # > 1000
            "transaction_type": "DEBIT"
        }
        
        category = service.categorize_transaction(transaction_data)
        
        assert category == categories["transporte"]  # High amount rule

    @pytest.mark.django_db
    def test_service_with_different_companies(self, user):
        """Should isolate rules by company"""
        company1 = Company.objects.create(
            name="Company 1",
            cnpj="11.111.111/0001-11",
            owner=user,
        )
        
        company2 = Company.objects.create(
            name="Company 2", 
            cnpj="22.222.222/0001-22",
            owner=user,
        )
        
        # Create categories for each company
        cat1 = Category.objects.create(company=company1, name="Category 1", color="#FF0000")
        cat2 = Category.objects.create(company=company2, name="Category 2", color="#00FF00")
        
        # Create rules for each company
        CategorizationRule.objects.create(
            company=company1,
            name="Rule 1",
            category=cat1,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=1,
        )
        
        CategorizationRule.objects.create(
            company=company2,
            name="Rule 2", 
            category=cat2,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=1,
        )
        
        service1 = CategorizationService(company1)
        service2 = CategorizationService(company2)
        
        assert service1.get_active_rules().count() == 1
        assert service2.get_active_rules().count() == 1
        assert service1.get_active_rules().first().category == cat1
        assert service2.get_active_rules().first().category == cat2