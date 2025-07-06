import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.categories.models import Category, CategorizationRule
from apps.categories.serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    CategorizationRuleSerializer,
    CategorizationRuleCreateSerializer,
)
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
def parent_category(company):
    return Category.objects.create(
        company=company,
        name="Receitas",
        color="#4CAF50",
        is_system=True,
    )


@pytest.fixture
def child_category(company, parent_category):
    return Category.objects.create(
        company=company,
        parent=parent_category,
        name="Salário",
        color="#8BC34A",
    )


@pytest.fixture
def categorization_rule(company, child_category):
    return CategorizationRule.objects.create(
        company=company,
        category=child_category,
        name="Regra Salário",
        condition_type="CONTAINS",
        field_name="description",
        field_value="salario",
        priority=10,
    )


class TestCategorySerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.parent_category = Category.objects.create(
            company=self.company,
            name="Receitas",
            color="#4CAF50",
            is_system=True,
        )
        self.child_category = Category.objects.create(
            company=self.company,
            parent=self.parent_category,
            name="Salário",
            color="#8BC34A",
        )

    def test_serialize_category_without_parent(self):
        """Should serialize parent category correctly"""
        serializer = CategorySerializer(self.parent_category)
        data = serializer.data

        assert data["id"] == self.parent_category.id
        assert data["company"] == self.company.id
        assert data["parent"] is None
        assert data["name"] == "Receitas"
        assert data["color"] == "#4CAF50"
        assert data["is_system"] is True
        assert data["is_active"] is True
        assert data["full_path"] == "Receitas"
        assert data["children_count"] == 1

    def test_serialize_category_with_parent(self):
        """Should serialize child category with parent info"""
        serializer = CategorySerializer(self.child_category)
        data = serializer.data

        assert data["id"] == self.child_category.id
        assert data["parent"]["id"] == self.parent_category.id
        assert data["parent"]["name"] == "Receitas"
        assert data["name"] == "Salário"
        assert data["color"] == "#8BC34A"
        assert data["is_system"] is False
        assert data["full_path"] == "Receitas > Salário"
        assert data["children_count"] == 0

    def test_serialize_category_with_rules_count(self):
        """Should include rules count in serialization"""
        # Add a categorization rule
        CategorizationRule.objects.create(
            company=self.company,
            category=self.child_category,
            name="Test Rule",
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
            priority=5,
        )

        serializer = CategorySerializer(self.child_category)
        data = serializer.data

        assert data["rules_count"] == 1

    def test_serialize_multiple_categories(self):
        """Should serialize multiple categories with proper ordering"""
        Category.objects.create(
            company=self.company,
            name="Despesas",
            color="#F44336",
        )

        categories = Category.objects.all().order_by("name")
        serializer = CategorySerializer(categories, many=True)
        data = serializer.data

        assert len(data) == 3
        assert data[0]["name"] == "Despesas"
        assert data[1]["name"] == "Receitas"
        assert data[2]["name"] == "Salário"


class TestCategoryCreateSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.parent_category = Category.objects.create(
            company=self.company,
            name="Receitas",
            color="#4CAF50",
        )

    def test_create_category_valid_data(self):
        """Should create category with valid data"""
        data = {
            "company": self.company.id,
            "name": "Nova Categoria",
            "color": "#2196F3",
            "is_system": False,
        }

        serializer = CategoryCreateSerializer(data=data)
        assert serializer.is_valid()

        category = serializer.save()
        assert category.company == self.company
        assert category.name == "Nova Categoria"
        assert category.color == "#2196F3"
        assert category.is_system is False
        assert category.is_active is True
        assert category.parent is None

    def test_create_category_with_parent(self):
        """Should create category with parent"""
        data = {
            "company": self.company.id,
            "parent": self.parent_category.id,
            "name": "Subcategoria",
            "color": "#9C27B0",
        }

        serializer = CategoryCreateSerializer(data=data)
        assert serializer.is_valid()

        category = serializer.save()
        assert category.parent == self.parent_category
        assert category.name == "Subcategoria"

    def test_create_category_duplicate_name_same_company(self):
        """Should reject duplicate name in same company"""
        data = {
            "company": self.company.id,
            "name": "Receitas",  # Same as existing
            "color": "#FF5722",
        }

        serializer = CategoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_create_category_invalid_color(self):
        """Should reject invalid hex color"""
        data = {
            "company": self.company.id,
            "name": "Test Category",
            "color": "invalid-color",
        }

        serializer = CategoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "color" in serializer.errors

    def test_create_category_missing_required_fields(self):
        """Should require company and name"""
        data = {}

        serializer = CategoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "company" in serializer.errors
        assert "name" in serializer.errors


class TestCategorizationRuleSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.category = Category.objects.create(
            company=self.company,
            name="Alimentação",
            color="#FF9800",
        )
        self.rule = CategorizationRule.objects.create(
            company=self.company,
            category=self.category,
            name="Supermercado Rule",
            condition_type="CONTAINS",
            field_name="description",
            field_value="supermercado",
            priority=10,
        )

    def test_serialize_categorization_rule(self):
        """Should serialize categorization rule correctly"""
        serializer = CategorizationRuleSerializer(self.rule)
        data = serializer.data

        assert data["id"] == self.rule.id
        assert data["company"] == self.company.id
        assert data["category"]["id"] == self.category.id
        assert data["category"]["name"] == "Alimentação"
        assert data["name"] == "Supermercado Rule"
        assert data["condition_type"] == "CONTAINS"
        assert data["field_name"] == "description"
        assert data["field_value"] == "supermercado"
        assert data["priority"] == 10
        assert data["is_active"] is True

    def test_serialize_rule_with_condition_display(self):
        """Should include human-readable condition display"""
        serializer = CategorizationRuleSerializer(self.rule)
        data = serializer.data

        assert data["condition_display"] == "Contains"
        assert data["field_display"] == "Description"

    def test_serialize_multiple_rules(self):
        """Should serialize multiple rules with proper ordering"""
        CategorizationRule.objects.create(
            company=self.company,
            category=self.category,
            name="High Priority Rule",
            condition_type="EQUALS",
            field_name="description",
            field_value="high priority",
            priority=20,
        )

        rules = CategorizationRule.objects.all().order_by("-priority", "name")
        serializer = CategorizationRuleSerializer(rules, many=True)
        data = serializer.data

        assert len(data) == 2
        assert data[0]["priority"] == 20
        assert data[1]["priority"] == 10


class TestCategorizationRuleCreateSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.category = Category.objects.create(
            company=self.company,
            name="Despesas",
            color="#F44336",
        )

    def test_create_rule_valid_data(self):
        """Should create categorization rule with valid data"""
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Nova Regra",
            "condition_type": "STARTS_WITH",
            "field_name": "description",
            "field_value": "compra",
            "priority": 15,
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert serializer.is_valid()

        rule = serializer.save()
        assert rule.company == self.company
        assert rule.category == self.category
        assert rule.name == "Nova Regra"
        assert rule.condition_type == "STARTS_WITH"
        assert rule.field_name == "description"
        assert rule.field_value == "compra"
        assert rule.priority == 15
        assert rule.is_active is True

    def test_create_rule_duplicate_name_same_company(self):
        """Should reject duplicate rule name in same company"""
        CategorizationRule.objects.create(
            company=self.company,
            category=self.category,
            name="Existing Rule",
            condition_type="CONTAINS",
            field_name="description",
            field_value="test",
        )

        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Existing Rule",  # Duplicate
            "condition_type": "EQUALS",
            "field_name": "amount",
            "field_value": "100",
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_create_rule_invalid_condition_type(self):
        """Should reject invalid condition type"""
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Test Rule",
            "condition_type": "INVALID_TYPE",
            "field_name": "description",
            "field_value": "test",
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "condition_type" in serializer.errors

    def test_create_rule_invalid_field_name(self):
        """Should reject invalid field name"""
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Test Rule",
            "condition_type": "CONTAINS",
            "field_name": "invalid_field",
            "field_value": "test",
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "field_name" in serializer.errors

    def test_create_rule_missing_required_fields(self):
        """Should require all necessary fields"""
        data = {
            "name": "Incomplete Rule",
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "company" in serializer.errors
        assert "category" in serializer.errors
        assert "condition_type" in serializer.errors
        assert "field_name" in serializer.errors
        assert "field_value" in serializer.errors

    def test_validate_regex_pattern(self):
        """Should validate regex patterns for REGEX condition type"""
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Regex Rule",
            "condition_type": "REGEX",
            "field_name": "description",
            "field_value": "[invalid regex",  # Invalid regex
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "field_value" in serializer.errors

    def test_validate_numeric_values_for_amount_field(self):
        """Should validate numeric values for amount-based conditions"""
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Amount Rule",
            "condition_type": "GREATER_THAN",
            "field_name": "amount",
            "field_value": "not_a_number",
        }

        serializer = CategorizationRuleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "field_value" in serializer.errors