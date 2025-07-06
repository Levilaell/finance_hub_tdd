from django.test import TestCase
from django.urls import reverse, resolve
from apps.categories.views import CategoryViewSet, CategorizationRuleViewSet


class TestCategoriesURLs(TestCase):
    """Test Categories URL patterns"""

    def test_categories_list_url(self):
        """Should resolve categories list URL"""
        url = reverse("categories:categories-list")
        assert url == "/api/categories/categories/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-list"

    def test_categories_detail_url(self):
        """Should resolve categories detail URL"""
        url = reverse("categories:categories-detail", kwargs={"pk": 1})
        assert url == "/api/categories/categories/1/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-detail"

    def test_categories_tree_url(self):
        """Should resolve categories tree URL"""
        url = reverse("categories:categories-tree")
        assert url == "/api/categories/categories/tree/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-tree"

    def test_categories_system_url(self):
        """Should resolve categories system URL"""
        url = reverse("categories:categories-system")
        assert url == "/api/categories/categories/system/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-system"

    def test_categories_create_defaults_url(self):
        """Should resolve categories create defaults URL"""
        url = reverse("categories:categories-create-defaults")
        assert url == "/api/categories/categories/create_defaults/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-create-defaults"

    def test_categories_bulk_toggle_url(self):
        """Should resolve categories bulk toggle URL"""
        url = reverse("categories:categories-bulk-toggle")
        assert url == "/api/categories/categories/bulk_toggle/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategoryViewSet
        assert resolver.url_name == "categories-bulk-toggle"

    def test_rules_list_url(self):
        """Should resolve rules list URL"""
        url = reverse("categories:rules-list")
        assert url == "/api/categories/rules/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategorizationRuleViewSet
        assert resolver.url_name == "rules-list"

    def test_rules_detail_url(self):
        """Should resolve rules detail URL"""
        url = reverse("categories:rules-detail", kwargs={"pk": 1})
        assert url == "/api/categories/rules/1/"
        
        resolver = resolve(url)
        assert resolver.func.cls == CategorizationRuleViewSet
        assert resolver.url_name == "rules-detail"