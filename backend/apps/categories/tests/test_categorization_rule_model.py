import pytest
from django.db import IntegrityError, transaction as db_transaction
from django.core.exceptions import ValidationError
from apps.categories.models import CategorizationRule, Category
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
def category(company):
    return Category.objects.create(
        company=company,
        name="Alimentação",
        color="#FF5722",
    )


class TestCategorizationRuleModel:
    """Test suite for CategorizationRule model"""

    @pytest.mark.django_db
    def test_create_categorization_rule(self, company, category):
        """Should create a categorization rule with required fields"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Regra Supermercado",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="supermercado",
            priority=10,
            is_active=True,
        )

        assert rule.company == company
        assert rule.name == "Regra Supermercado"
        assert rule.category == category
        assert rule.condition_type == "CONTAINS"
        assert rule.field_name == "description"
        assert rule.field_value == "supermercado"
        assert rule.priority == 10
        assert rule.is_active is True
        assert rule.created_at is not None
        assert rule.updated_at is not None

    @pytest.mark.django_db
    def test_categorization_rule_str_representation(self, company, category):
        """Should return formatted string representation"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Regra Restaurante",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="restaurante",
        )

        assert str(rule) == "Regra Restaurante"

    @pytest.mark.django_db
    def test_condition_types(self, company, category):
        """Should support different condition types"""
        # CONTAINS
        rule_contains = CategorizationRule.objects.create(
            company=company,
            name="Contains Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="mercado",
        )

        # EQUALS
        rule_equals = CategorizationRule.objects.create(
            company=company,
            name="Equals Rule",
            category=category,
            condition_type="EQUALS",
            field_name="description",
            field_value="Compra no Mercado",
        )

        # STARTS_WITH
        rule_starts = CategorizationRule.objects.create(
            company=company,
            name="Starts Rule",
            category=category,
            condition_type="STARTS_WITH",
            field_name="description",
            field_value="PIX",
        )

        # ENDS_WITH
        rule_ends = CategorizationRule.objects.create(
            company=company,
            name="Ends Rule",
            category=category,
            condition_type="ENDS_WITH",
            field_name="description",
            field_value="LTDA",
        )

        # REGEX
        rule_regex = CategorizationRule.objects.create(
            company=company,
            name="Regex Rule",
            category=category,
            condition_type="REGEX",
            field_name="description",
            field_value=r".*\d{4}.*",
        )

        assert rule_contains.condition_type == "CONTAINS"
        assert rule_equals.condition_type == "EQUALS"
        assert rule_starts.condition_type == "STARTS_WITH"
        assert rule_ends.condition_type == "ENDS_WITH"
        assert rule_regex.condition_type == "REGEX"

    @pytest.mark.django_db
    def test_field_names(self, company, category):
        """Should support different field names"""
        # Description field
        rule_desc = CategorizationRule.objects.create(
            company=company,
            name="Description Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        # Amount field
        rule_amount = CategorizationRule.objects.create(
            company=company,
            name="Amount Rule",
            category=category,
            condition_type="GREATER_THAN",
            field_name="amount",
            field_value="100.00",
        )

        # Transaction type field
        rule_type = CategorizationRule.objects.create(
            company=company,
            name="Type Rule",
            category=category,
            condition_type="EQUALS",
            field_name="transaction_type",
            field_value="DEBIT",
        )

        assert rule_desc.field_name == "description"
        assert rule_amount.field_name == "amount"
        assert rule_type.field_name == "transaction_type"

    @pytest.mark.django_db
    def test_rule_priority_ordering(self, company, category):
        """Should order rules by priority (higher priority first)"""
        rule_low = CategorizationRule.objects.create(
            company=company,
            name="Low Priority",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=1,
        )

        rule_high = CategorizationRule.objects.create(
            company=company,
            name="High Priority",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=10,
        )

        rule_medium = CategorizationRule.objects.create(
            company=company,
            name="Medium Priority",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=5,
        )

        rules = CategorizationRule.objects.filter(company=company)
        priorities = [r.priority for r in rules]

        assert priorities == [10, 5, 1]  # Descending order

    @pytest.mark.django_db
    def test_rule_unique_name_per_company(self, company, category, user):
        """Should enforce unique rule name per company"""
        CategorizationRule.objects.create(
            company=company,
            name="Unique Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        # Same name in same company should fail
        with pytest.raises(IntegrityError):
            with db_transaction.atomic():
                CategorizationRule.objects.create(
                    company=company,
                    name="Unique Rule",  # Same name
                    category=category,
                    condition_type="CONTAINS",
                    field_name="description",
                    field_value="other",
                )

        # Same name in different company should work
        other_company = Company.objects.create(
            name="Other Company",
            cnpj="22.333.444/0001-55",
            owner=user,
        )

        other_category = Category.objects.create(
            company=other_company,
            name="Other Category",
            color="#4CAF50",
        )

        CategorizationRule.objects.create(
            company=other_company,
            name="Unique Rule",  # Same name, different company
            category=other_category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

    @pytest.mark.django_db
    def test_rule_default_values(self, company, category):
        """Should set default values correctly"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Default Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        assert rule.priority == 1
        assert rule.is_active is True

    @pytest.mark.django_db
    def test_get_active_rules(self, company, category):
        """Should filter only active rules"""
        active_rule = CategorizationRule.objects.create(
            company=company,
            name="Active Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="active",
            is_active=True,
        )

        inactive_rule = CategorizationRule.objects.create(
            company=company,
            name="Inactive Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="inactive",
            is_active=False,
        )

        active_rules = CategorizationRule.objects.filter(company=company, is_active=True)

        assert active_rule in active_rules
        assert inactive_rule not in active_rules
        assert active_rules.count() == 1

    @pytest.mark.django_db
    def test_category_cascade_delete(self, company, category):
        """Should delete rules when category is deleted"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Test Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        category.delete()

        assert CategorizationRule.objects.filter(id=rule.id).exists() is False

    @pytest.mark.django_db
    def test_company_cascade_delete(self, company, category):
        """Should delete rules when company is deleted"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Test Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        company.delete()

        assert CategorizationRule.objects.filter(id=rule.id).exists() is False

    @pytest.mark.django_db
    def test_matches_transaction_description_contains(self, company, category):
        """Should match transaction using CONTAINS condition"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Supermercado Rule",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="supermercado",
        )

        # Should match
        assert rule.matches_transaction({
            "description": "Compra no supermercado",
            "amount": 50.00,
            "transaction_type": "DEBIT"
        }) is True

        assert rule.matches_transaction({
            "description": "SUPERMERCADO EXTRA",
            "amount": 75.00,
            "transaction_type": "DEBIT"
        }) is True

        # Should not match
        assert rule.matches_transaction({
            "description": "Compra na farmácia",
            "amount": 30.00,
            "transaction_type": "DEBIT"
        }) is False

    @pytest.mark.django_db
    def test_matches_transaction_amount_greater_than(self, company, category):
        """Should match transaction using GREATER_THAN condition for amount"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="High Value Rule",
            category=category,
            condition_type="GREATER_THAN",
            field_name="amount",
            field_value="100.00",
        )

        # Should match
        assert rule.matches_transaction({
            "description": "Compra cara",
            "amount": 150.00,
            "transaction_type": "DEBIT"
        }) is True

        # Should not match
        assert rule.matches_transaction({
            "description": "Compra barata",
            "amount": 50.00,
            "transaction_type": "DEBIT"
        }) is False

        # Equal should not match
        assert rule.matches_transaction({
            "description": "Compra igual",
            "amount": 100.00,
            "transaction_type": "DEBIT"
        }) is False

    @pytest.mark.django_db
    def test_matches_transaction_regex(self, company, category):
        """Should match transaction using REGEX condition"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="PIX Rule",
            category=category,
            condition_type="REGEX",
            field_name="description",
            field_value=r"^PIX.*\d{4}",
        )

        # Should match
        assert rule.matches_transaction({
            "description": "PIX para João 1234",
            "amount": 100.00,
            "transaction_type": "DEBIT"
        }) is True

        # Should not match
        assert rule.matches_transaction({
            "description": "TED para João",
            "amount": 100.00,
            "transaction_type": "DEBIT"
        }) is False

        # Should not match (no numbers)
        assert rule.matches_transaction({
            "description": "PIX para João",
            "amount": 100.00,
            "transaction_type": "DEBIT"
        }) is False

    @pytest.mark.django_db
    def test_get_rules_for_company_ordered(self, company, category):
        """Should get rules for company ordered by priority"""
        rule1 = CategorizationRule.objects.create(
            company=company,
            name="Rule 1",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test1",
            priority=5,
        )

        rule2 = CategorizationRule.objects.create(
            company=company,
            name="Rule 2",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test2",
            priority=10,
        )

        rule3 = CategorizationRule.objects.create(
            company=company,
            name="Rule 3",
            category=category,
            condition_type="CONTAINS",
            field_name="description",
            field_value="test3",
            priority=1,
        )

        rules = CategorizationRule.objects.filter(company=company, is_active=True)
        rule_names = [r.name for r in rules]

        assert rule_names == ["Rule 2", "Rule 1", "Rule 3"]  # By priority desc

    @pytest.mark.django_db
    def test_invalid_regex_handling(self, company, category):
        """Should handle invalid regex patterns gracefully"""
        rule = CategorizationRule.objects.create(
            company=company,
            name="Invalid Regex Rule",
            category=category,
            condition_type="REGEX",
            field_name="description",
            field_value="[invalid regex",  # Invalid regex
        )

        # Should not crash, should return False for invalid regex
        assert rule.matches_transaction({
            "description": "Any description",
            "amount": 100.00,
            "transaction_type": "DEBIT"
        }) is False