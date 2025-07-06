from rest_framework.permissions import BasePermission
from apps.companies.models import CompanyUser


class IsCategoryOwner(BasePermission):
    """
    Permission to only allow owners of categories to view/edit them.
    Checks if the user is a member of the company that owns the category.
    """

    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False

        # Verificar se é proprietário da empresa (automaticamente tem acesso)
        if obj.company.owner == request.user:
            return True

        # Verificar se é membro ativo da empresa
        return CompanyUser.objects.filter(
            company=obj.company,
            user=request.user,
            is_active=True
        ).exists()


class IsRuleOwner(BasePermission):
    """
    Permission to only allow owners of categorization rules to view/edit them.
    Checks if the user is a member of the company that owns the rule.
    """

    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False

        # Verificar se é proprietário da empresa (automaticamente tem acesso)
        if obj.company.owner == request.user:
            return True

        # Verificar se é membro ativo da empresa
        return CompanyUser.objects.filter(
            company=obj.company,
            user=request.user,
            is_active=True
        ).exists()