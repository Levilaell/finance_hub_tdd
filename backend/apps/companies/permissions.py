from rest_framework.permissions import BasePermission
from .models import CompanyUser, Subscription


class IsCompanyOwner(BasePermission):
    """
    Permissão que permite acesso apenas ao proprietário da empresa.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se o usuário é o proprietário da empresa
        return obj.owner == request.user


class IsCompanyMember(BasePermission):
    """
    Permissão que permite acesso a membros da empresa.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é o proprietário (automaticamente membro)
        if obj.owner == request.user:
            return True
        
        # Verificar se é membro através da tabela CompanyUser
        return CompanyUser.objects.filter(
            company=obj,
            user=request.user,
            is_active=True
        ).exists()


class IsCompanyAdminOrOwner(BasePermission):
    """
    Permissão que permite acesso apenas a admins ou proprietários da empresa.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar se é o proprietário
        if obj.owner == request.user:
            return True
        
        # Verificar se é admin da empresa
        return CompanyUser.objects.filter(
            company=obj,
            user=request.user,
            role__in=['admin'],
            is_active=True
        ).exists()


class CompanyResourcePermission(BasePermission):
    """
    Permissão para recursos que pertencem a uma empresa.
    Verifica se o usuário é membro da empresa que possui o recurso.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Obter a empresa do objeto (assume que o objeto tem atributo 'company')
        company = getattr(obj, 'company', None)
        if not company:
            return False
        
        # Verificar se é o proprietário da empresa
        if company.owner == request.user:
            return True
        
        # Verificar se é membro da empresa
        return CompanyUser.objects.filter(
            company=company,
            user=request.user,
            is_active=True
        ).exists()


class IsCompanyActive(BasePermission):
    """
    Permissão que verifica se a empresa está ativa.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verificar se a empresa está ativa
        return obj.is_active


class HasSubscriptionFeature(BasePermission):
    """
    Permissão que verifica se a assinatura da empresa possui uma feature específica.
    """
    
    def __init__(self, required_feature):
        self.required_feature = required_feature
    
    def has_object_permission(self, request, view, obj):
        try:
            # Obter a assinatura ativa da empresa
            subscription = Subscription.objects.get(
                company=obj,
                status__in=['trial', 'active']
            )
            
            # Verificar se o plano possui a feature necessária
            return self.required_feature in subscription.plan.features
            
        except Subscription.DoesNotExist:
            return False