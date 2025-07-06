from django.db import models
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Company, CompanyUser, SubscriptionPlan, Subscription
from .serializers import (
    CompanySerializer, 
    CompanyCreateSerializer,
    CompanyUserSerializer,
    CompanyUserCreateSerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer
)
from .permissions import (
    IsCompanyOwner,
    IsCompanyMember,
    IsCompanyAdminOrOwner,
    IsCompanyActive
)


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de empresas"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'company_type']
    
    def get_queryset(self):
        """Retornar apenas empresas que o usuário tem acesso"""
        user = self.request.user
        return Company.objects.filter(
            models.Q(owner=user) | 
            models.Q(users=user)
        ).distinct()
    
    def get_serializer_class(self):
        """Usar serializer específico para criação"""
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer
    
    def create(self, request, *args, **kwargs):
        """Criar empresa e retornar dados completos"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Retornar dados usando o CompanySerializer
        response_serializer = CompanySerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        """Definir permissões específicas por ação"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]
        elif self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class CompanyUserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de usuários da empresa"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar serializer específico para criação"""
        if self.action == 'create':
            return CompanyUserCreateSerializer
        return CompanyUserSerializer
    
    def get_queryset(self):
        """Retornar membros da empresa específica"""
        company_id = self.kwargs.get('company_pk')
        return CompanyUser.objects.filter(
            company_id=company_id,
            is_active=True
        ).select_related('user', 'company')
    
    def perform_create(self, serializer):
        """Associar empresa ao criar membro"""
        company_id = self.kwargs.get('company_pk')
        company = Company.objects.get(id=company_id)
        serializer.save(company=company)
    
    def get_permissions(self):
        """Definir permissões específicas por ação"""
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualização de planos de assinatura"""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = []  # Público
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['max_companies']
    ordering = ['price']


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de assinaturas"""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retornar assinaturas das empresas do usuário"""
        user = self.request.user
        return Subscription.objects.filter(
            company__owner=user
        ).select_related('company', 'plan')
    
    def get_permissions(self):
        """Definir permissões específicas por ação"""
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
