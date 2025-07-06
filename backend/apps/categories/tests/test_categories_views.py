import pytest
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.companies.models import Company, CompanyUser
from apps.categories.models import Category, CategorizationRule


@pytest.fixture
def api_client():
    return APIClient()


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
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


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


class TestCategoryViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        # Create test categories
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

    def test_list_categories_for_company(self):
        """Should list categories for user's company"""
        url = reverse("categories:categories-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Should be ordered by name
        assert response.data["results"][0]["name"] == "Receitas"
        assert response.data["results"][1]["name"] == "Salário"

    def test_list_categories_filters_by_company(self):
        """Should only show categories for user's company"""
        # Create another company and category
        other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123!"
        )
        other_company = Company.objects.create(
            name="Other Company", cnpj="22.333.444/0001-82", owner=other_user
        )
        Category.objects.create(
            company=other_company,
            name="Other Category",
            color="#FF5722",
        )

        url = reverse("categories:categories-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Only user's categories

    def test_create_category(self):
        """Should create new category"""
        url = reverse("categories:categories-list")
        data = {
            "company": self.company.id,
            "name": "Nova Categoria",
            "color": "#2196F3",
            "is_system": False,
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Nova Categoria"
        assert response.data["color"] == "#2196F3"
        assert response.data["is_system"] is False

        # Verify category was created in database
        assert Category.objects.filter(name="Nova Categoria").exists()

    def test_create_category_with_parent(self):
        """Should create category with parent"""
        url = reverse("categories:categories-list")
        data = {
            "company": self.company.id,
            "parent": self.parent_category.id,
            "name": "Subcategoria",
            "color": "#9C27B0",
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["parent"]["id"] == self.parent_category.id
        assert response.data["full_path"] == "Receitas > Subcategoria"

    def test_retrieve_category(self):
        """Should retrieve specific category"""
        url = reverse("categories:categories-detail", kwargs={"pk": self.child_category.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Salário"
        assert response.data["parent"]["name"] == "Receitas"
        assert response.data["full_path"] == "Receitas > Salário"

    def test_update_category(self):
        """Should update category"""
        url = reverse("categories:categories-detail", kwargs={"pk": self.child_category.pk})
        data = {
            "name": "Salário Atualizado",
            "color": "#4CAF50",
        }

        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Salário Atualizado"
        assert response.data["color"] == "#4CAF50"

    def test_delete_category(self):
        """Should delete category"""
        url = reverse("categories:categories-detail", kwargs={"pk": self.child_category.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=self.child_category.pk).exists()

    def test_filter_categories_by_parent(self):
        """Should filter categories by parent"""
        url = reverse("categories:categories-list")
        response = self.client.get(url, {"parent": self.parent_category.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Salário"

    def test_filter_categories_by_is_system(self):
        """Should filter categories by is_system"""
        url = reverse("categories:categories-list")
        response = self.client.get(url, {"is_system": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Receitas"

    def test_search_categories_by_name(self):
        """Should search categories by name"""
        url = reverse("categories:categories-list")
        response = self.client.get(url, {"search": "salário"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Salário"

    def test_category_requires_authentication(self):
        """Should require authentication to access categories"""
        self.client.force_authenticate(user=None)
        url = reverse("categories:categories-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCategorizationRuleViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            company=self.company,
            name="Alimentação",
            color="#FF9800",
        )

        # Create test rules
        self.rule1 = CategorizationRule.objects.create(
            company=self.company,
            category=self.category,
            name="Supermercado Rule",
            condition_type="CONTAINS",
            field_name="description",
            field_value="supermercado",
            priority=10,
        )
        self.rule2 = CategorizationRule.objects.create(
            company=self.company,
            category=self.category,
            name="High Priority Rule",
            condition_type="EQUALS",
            field_name="description",
            field_value="padaria",
            priority=20,
        )

    def test_list_categorization_rules_for_company(self):
        """Should list categorization rules for user's company"""
        url = reverse("categories:rules-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Should be ordered by priority desc, then name
        assert response.data["results"][0]["priority"] == 20
        assert response.data["results"][1]["priority"] == 10

    def test_list_rules_filters_by_company(self):
        """Should only show rules for user's company"""
        # Create another company and rule
        other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123!"
        )
        other_company = Company.objects.create(
            name="Other Company", cnpj="22.333.444/0001-82", owner=other_user
        )
        other_category = Category.objects.create(
            company=other_company,
            name="Other Category",
            color="#F44336",
        )
        CategorizationRule.objects.create(
            company=other_company,
            category=other_category,
            name="Other Rule",
            condition_type="CONTAINS",
            field_name="description",
            field_value="other",
        )

        url = reverse("categories:rules-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Only user's rules

    def test_create_categorization_rule(self):
        """Should create new categorization rule"""
        url = reverse("categories:rules-list")
        data = {
            "company": self.company.id,
            "category": self.category.id,
            "name": "Nova Regra",
            "condition_type": "STARTS_WITH",
            "field_name": "description",
            "field_value": "compra",
            "priority": 15,
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Nova Regra"
        assert response.data["condition_type"] == "STARTS_WITH"
        assert response.data["priority"] == 15

        # Verify rule was created in database
        assert CategorizationRule.objects.filter(name="Nova Regra").exists()

    def test_retrieve_categorization_rule(self):
        """Should retrieve specific categorization rule"""
        url = reverse("categories:rules-detail", kwargs={"pk": self.rule1.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Supermercado Rule"
        assert response.data["category"]["name"] == "Alimentação"
        assert response.data["condition_display"] == "Contains"

    def test_update_categorization_rule(self):
        """Should update categorization rule"""
        url = reverse("categories:rules-detail", kwargs={"pk": self.rule1.pk})
        data = {
            "name": "Supermercado Atualizado",
            "priority": 25,
        }

        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Supermercado Atualizado"
        assert response.data["priority"] == 25

    def test_delete_categorization_rule(self):
        """Should delete categorization rule"""
        url = reverse("categories:rules-detail", kwargs={"pk": self.rule1.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CategorizationRule.objects.filter(pk=self.rule1.pk).exists()

    def test_filter_rules_by_category(self):
        """Should filter rules by category"""
        url = reverse("categories:rules-list")
        response = self.client.get(url, {"category": self.category.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        for rule in response.data["results"]:
            assert rule["category"]["id"] == self.category.id

    def test_filter_rules_by_condition_type(self):
        """Should filter rules by condition type"""
        url = reverse("categories:rules-list")
        response = self.client.get(url, {"condition_type": "CONTAINS"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["condition_type"] == "CONTAINS"

    def test_search_rules_by_name(self):
        """Should search rules by name"""
        url = reverse("categories:rules-list")
        response = self.client.get(url, {"search": "supermercado"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Supermercado Rule"

    def test_rule_requires_authentication(self):
        """Should require authentication to access rules"""
        self.client.force_authenticate(user=None)
        url = reverse("categories:rules-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCategoryActionViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test"
        )
        self.company = Company.objects.create(
            name="Test Company", cnpj="11.222.333/0001-81", owner=self.user
        )
        self.client.force_authenticate(user=self.user)

        self.parent_category = Category.objects.create(
            company=self.company,
            name="Receitas",
            color="#4CAF50",
        )
        self.child_category = Category.objects.create(
            company=self.company,
            parent=self.parent_category,
            name="Salário",
            color="#8BC34A",
        )

    def test_get_category_tree(self):
        """Should return hierarchical category tree"""
        url = reverse("categories:categories-tree")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "tree" in response.data
        assert len(response.data["tree"]) == 1  # Only root categories

        root_category = response.data["tree"][0]
        assert root_category["name"] == "Receitas"
        assert len(root_category["children"]) == 1
        assert root_category["children"][0]["name"] == "Salário"

    def test_get_system_categories(self):
        """Should return only system categories"""
        # Mark parent as system category
        self.parent_category.is_system = True
        self.parent_category.save()

        url = reverse("categories:categories-system")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Receitas"
        assert response.data[0]["is_system"] is True

    def test_bulk_create_default_categories(self):
        """Should create default category structure"""
        # Clear existing categories
        Category.objects.filter(company=self.company).delete()

        url = reverse("categories:categories-create-defaults")
        response = self.client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert "created_categories" in response.data
        assert response.data["created_count"] > 0

        # Verify categories were created
        categories = Category.objects.filter(company=self.company)
        assert categories.exists()

    def test_bulk_activate_deactivate_categories(self):
        """Should bulk activate/deactivate categories"""
        url = reverse("categories:categories-bulk-toggle")
        data = {
            "category_ids": [self.parent_category.id, self.child_category.id],
            "is_active": False,
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["updated_count"] == 2

        # Verify categories were deactivated
        self.parent_category.refresh_from_db()
        self.child_category.refresh_from_db()
        assert not self.parent_category.is_active
        assert not self.child_category.is_active