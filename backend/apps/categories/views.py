from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.banking.permissions import IsBankAccountOwner  # Reusar permission logic similar
from .models import Category, CategorizationRule
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    CategorizationRuleSerializer,
    CategorizationRuleCreateSerializer,
)
from .permissions import IsCategoryOwner, IsRuleOwner


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category with company filtering"""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsCategoryOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["parent", "is_system", "is_active"]
    search_fields = ["name"]

    def get_queryset(self):
        """Filter categories by user's companies"""
        user_companies = self.request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        return Category.objects.filter(company__in=user_companies).order_by("name")

    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == "create":
            return CategoryCreateSerializer
        return CategorySerializer

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Get hierarchical category tree"""
        user_companies = request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        
        # Get root categories (no parent)
        root_categories = Category.objects.filter(
            company__in=user_companies,
            parent__isnull=True,
            is_active=True
        ).order_by("name")

        def build_tree(categories):
            tree = []
            for category in categories:
                category_data = CategorySerializer(category).data
                children = Category.objects.filter(
                    parent=category, is_active=True
                ).order_by("name")
                if children.exists():
                    category_data["children"] = build_tree(children)
                else:
                    category_data["children"] = []
                tree.append(category_data)
            return tree

        tree = build_tree(root_categories)
        return Response({"tree": tree})

    @action(detail=False, methods=["get"])
    def system(self, request):
        """Get only system categories"""
        user_companies = request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        
        system_categories = Category.objects.filter(
            company__in=user_companies,
            is_system=True,
            is_active=True
        ).order_by("name")

        serializer = CategorySerializer(system_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def create_defaults(self, request):
        """Create default category structure for company"""
        user_companies = request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        
        if not user_companies:
            return Response(
                {"error": "No company found for user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_id = user_companies.first()
        
        # Default categories structure
        default_categories = [
            {"name": "Receitas", "color": "#4CAF50", "is_system": True},
            {"name": "Despesas", "color": "#F44336", "is_system": True},
            {"name": "Transferências", "color": "#2196F3", "is_system": True},
        ]

        created_categories = []
        for cat_data in default_categories:
            category, created = Category.objects.get_or_create(
                company_id=company_id,
                name=cat_data["name"],
                defaults=cat_data
            )
            if created:
                created_categories.append(CategorySerializer(category).data)

        return Response(
            {
                "created_categories": created_categories,
                "created_count": len(created_categories)
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def bulk_toggle(self, request):
        """Bulk activate/deactivate categories"""
        category_ids = request.data.get("category_ids", [])
        is_active = request.data.get("is_active", True)

        if not category_ids:
            return Response(
                {"error": "category_ids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_companies = request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)

        updated_count = Category.objects.filter(
            id__in=category_ids,
            company__in=user_companies
        ).update(is_active=is_active)

        return Response({"updated_count": updated_count})


class CategorizationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for CategorizationRule with company filtering"""

    serializer_class = CategorizationRuleSerializer
    permission_classes = [IsAuthenticated, IsRuleOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "condition_type", "field_name", "is_active"]
    search_fields = ["name", "field_value"]

    def get_queryset(self):
        """Filter rules by user's companies"""
        user_companies = self.request.user.company_memberships.filter(
            is_active=True
        ).values_list("company", flat=True)
        return CategorizationRule.objects.filter(
            company__in=user_companies
        ).order_by("-priority", "name")

    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == "create":
            return CategorizationRuleCreateSerializer
        return CategorizationRuleSerializer