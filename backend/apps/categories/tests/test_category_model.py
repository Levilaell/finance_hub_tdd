import pytest
from django.db import IntegrityError, transaction as db_transaction
from django.core.exceptions import ValidationError
from apps.categories.models import Category
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


class TestCategoryModel:
    """Test suite for Category model"""

    @pytest.mark.django_db
    def test_create_category(self, company):
        """Should create a category with required fields"""
        category = Category.objects.create(
            company=company,
            name="Alimentação",
            color="#FF5722",
            is_system=False,
            is_active=True,
        )

        assert category.company == company
        assert category.name == "Alimentação"
        assert category.color == "#FF5722"
        assert category.parent is None
        assert category.is_system is False
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None

    @pytest.mark.django_db
    def test_category_str_representation(self, company):
        """Should return formatted string representation"""
        category = Category.objects.create(
            company=company,
            name="Transporte",
            color="#2196F3",
        )

        assert str(category) == "Transporte"

    @pytest.mark.django_db
    def test_create_subcategory(self, company):
        """Should create a subcategory with parent relationship"""
        parent_category = Category.objects.create(
            company=company,
            name="Alimentação",
            color="#FF5722",
        )

        subcategory = Category.objects.create(
            company=company,
            parent=parent_category,
            name="Restaurantes",
            color="#FF8A65",
        )

        assert subcategory.parent == parent_category
        assert subcategory.name == "Restaurantes"
        assert parent_category in subcategory.get_ancestors()

    @pytest.mark.django_db
    def test_category_unique_name_per_company(self, company, user):
        """Should enforce unique category name per company"""
        Category.objects.create(
            company=company,
            name="Alimentação",
            color="#FF5722",
        )

        # Same name in same company should fail
        with pytest.raises(IntegrityError):
            with db_transaction.atomic():
                Category.objects.create(
                    company=company,
                    name="Alimentação",  # Same name
                    color="#4CAF50",
                )

        # Same name in different company should work
        other_company = Company.objects.create(
            name="Other Company",
            cnpj="22.333.444/0001-55",
            owner=user,
        )

        Category.objects.create(
            company=other_company,
            name="Alimentação",  # Same name, different company
            color="#4CAF50",
        )

    @pytest.mark.django_db
    def test_category_default_values(self, company):
        """Should set default values correctly"""
        category = Category.objects.create(
            company=company,
            name="Test Category",
            color="#000000",
        )

        assert category.parent is None
        assert category.is_system is False
        assert category.is_active is True

    @pytest.mark.django_db
    def test_create_system_category(self, company):
        """Should create system categories"""
        system_category = Category.objects.create(
            company=company,
            name="Sem Categoria",
            color="#9E9E9E",
            is_system=True,
        )

        assert system_category.is_system is True
        assert system_category.name == "Sem Categoria"

    @pytest.mark.django_db
    def test_category_color_validation(self, company):
        """Should validate color format"""
        # Valid hex color
        category = Category.objects.create(
            company=company,
            name="Valid Color",
            color="#FF5722",
        )
        assert category.color == "#FF5722"

        # Invalid hex color should still save (validation in serializer)
        category2 = Category.objects.create(
            company=company,
            name="Invalid Color",
            color="red",  # Invalid hex
        )
        assert category2.color == "red"

    @pytest.mark.django_db
    def test_category_hierarchy_depth(self, company):
        """Should support multiple levels of hierarchy"""
        level1 = Category.objects.create(
            company=company,
            name="Despesas",
            color="#F44336",
        )

        level2 = Category.objects.create(
            company=company,
            parent=level1,
            name="Alimentação",
            color="#FF5722",
        )

        level3 = Category.objects.create(
            company=company,
            parent=level2,
            name="Restaurantes",
            color="#FF8A65",
        )

        assert level3.parent == level2
        assert level2.parent == level1
        assert level1.parent is None

    @pytest.mark.django_db
    def test_get_children(self, company):
        """Should get direct children of a category"""
        parent = Category.objects.create(
            company=company,
            name="Alimentação",
            color="#FF5722",
        )

        child1 = Category.objects.create(
            company=company,
            parent=parent,
            name="Restaurantes",
            color="#FF8A65",
        )

        child2 = Category.objects.create(
            company=company,
            parent=parent,
            name="Supermercado",
            color="#FFA726",
        )

        children = parent.get_children()
        assert child1 in children
        assert child2 in children
        assert children.count() == 2

    @pytest.mark.django_db
    def test_get_descendants(self, company):
        """Should get all descendants of a category"""
        grandparent = Category.objects.create(
            company=company,
            name="Despesas",
            color="#F44336",
        )

        parent = Category.objects.create(
            company=company,
            parent=grandparent,
            name="Alimentação",
            color="#FF5722",
        )

        child = Category.objects.create(
            company=company,
            parent=parent,
            name="Restaurantes",
            color="#FF8A65",
        )

        descendants = grandparent.get_descendants()
        assert parent in descendants
        assert child in descendants
        assert descendants.count() == 2

    @pytest.mark.django_db
    def test_get_ancestors(self, company):
        """Should get all ancestors of a category"""
        grandparent = Category.objects.create(
            company=company,
            name="Despesas",
            color="#F44336",
        )

        parent = Category.objects.create(
            company=company,
            parent=grandparent,
            name="Alimentação",
            color="#FF5722",
        )

        child = Category.objects.create(
            company=company,
            parent=parent,
            name="Restaurantes",
            color="#FF8A65",
        )

        ancestors = child.get_ancestors()
        assert parent in ancestors
        assert grandparent in ancestors
        assert ancestors.count() == 2

    @pytest.mark.django_db
    def test_get_root_categories(self, company):
        """Should get only root categories (no parent)"""
        root1 = Category.objects.create(
            company=company,
            name="Receitas",
            color="#4CAF50",
        )

        root2 = Category.objects.create(
            company=company,
            name="Despesas",
            color="#F44336",
        )

        child = Category.objects.create(
            company=company,
            parent=root2,
            name="Alimentação",
            color="#FF5722",
        )

        root_categories = Category.objects.filter(company=company, parent__isnull=True)
        assert root1 in root_categories
        assert root2 in root_categories
        assert child not in root_categories
        assert root_categories.count() == 2

    @pytest.mark.django_db
    def test_category_ordering(self, company):
        """Should order categories by name"""
        cat_c = Category.objects.create(
            company=company,
            name="C - Categoria",
            color="#000000",
        )

        cat_a = Category.objects.create(
            company=company,
            name="A - Categoria",
            color="#000000",
        )

        cat_b = Category.objects.create(
            company=company,
            name="B - Categoria",
            color="#000000",
        )

        categories = Category.objects.filter(company=company)
        names = [c.name for c in categories]

        assert names == ["A - Categoria", "B - Categoria", "C - Categoria"]

    @pytest.mark.django_db
    def test_get_active_categories(self, company):
        """Should filter only active categories"""
        active_category = Category.objects.create(
            company=company,
            name="Categoria Ativa",
            color="#4CAF50",
            is_active=True,
        )

        inactive_category = Category.objects.create(
            company=company,
            name="Categoria Inativa",
            color="#9E9E9E",
            is_active=False,
        )

        active_categories = Category.objects.filter(company=company, is_active=True)

        assert active_category in active_categories
        assert inactive_category not in active_categories
        assert active_categories.count() == 1

    @pytest.mark.django_db
    def test_prevent_self_parent(self, company):
        """Should prevent category from being its own parent"""
        category = Category.objects.create(
            company=company,
            name="Test Category",
            color="#000000",
        )

        # This should be handled at model level
        category.parent = category
        
        # The constraint should be enforced in clean() method
        with pytest.raises(ValidationError):
            category.full_clean()

    @pytest.mark.django_db
    def test_prevent_circular_reference(self, company):
        """Should prevent circular parent-child relationships"""
        parent = Category.objects.create(
            company=company,
            name="Parent",
            color="#000000",
        )

        child = Category.objects.create(
            company=company,
            parent=parent,
            name="Child",
            color="#000000",
        )

        # Try to make parent a child of its own child (circular)
        parent.parent = child
        
        with pytest.raises(ValidationError):
            parent.full_clean()

    @pytest.mark.django_db
    def test_company_cascade_delete(self, company):
        """Should delete categories when company is deleted"""
        category = Category.objects.create(
            company=company,
            name="Test Category",
            color="#000000",
        )

        company.delete()

        assert Category.objects.filter(id=category.id).exists() is False

    @pytest.mark.django_db
    def test_get_full_path(self, company):
        """Should get full hierarchical path of category"""
        grandparent = Category.objects.create(
            company=company,
            name="Despesas",
            color="#F44336",
        )

        parent = Category.objects.create(
            company=company,
            parent=grandparent,
            name="Alimentação",
            color="#FF5722",
        )

        child = Category.objects.create(
            company=company,
            parent=parent,
            name="Restaurantes",
            color="#FF8A65",
        )

        assert child.get_full_path() == "Despesas > Alimentação > Restaurantes"
        assert parent.get_full_path() == "Despesas > Alimentação"
        assert grandparent.get_full_path() == "Despesas"