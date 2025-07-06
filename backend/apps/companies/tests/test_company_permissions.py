import pytest
from unittest.mock import Mock
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory
from apps.companies.models import Company, CompanyUser, SubscriptionPlan, Subscription
from apps.companies.permissions import (
    IsCompanyOwner,
    IsCompanyMember, 
    IsCompanyAdminOrOwner,
    CompanyResourcePermission,
    IsCompanyActive,
    HasSubscriptionFeature
)

User = get_user_model()


@pytest.mark.django_db
class TestIsCompanyOwner:
    """Testes para permissão IsCompanyOwner"""
    
    def test_company_owner_has_permission(self, company, owner):
        """Proprietário da empresa deve ter permissão"""
        # Arrange
        permission = IsCompanyOwner()
        request = Mock()
        request.user = owner
        view = Mock()
        view.get_object.return_value = company
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is True
    
    def test_non_owner_has_no_permission(self, company, admin_user):
        """Usuário que não é proprietário não deve ter permissão"""
        # Arrange
        permission = IsCompanyOwner()
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is False
    
    def test_anonymous_user_has_no_permission(self, company):
        """Usuário anônimo não deve ter permissão"""
        # Arrange
        permission = IsCompanyOwner()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is False


@pytest.mark.django_db
class TestIsCompanyMember:
    """Testes para permissão IsCompanyMember"""
    
    def test_company_member_has_permission(self, company, admin_user):
        """Membro da empresa deve ter permissão"""
        # Arrange
        CompanyUser.objects.create(
            company=company,
            user=admin_user,
            role='admin'
        )
        permission = IsCompanyMember()
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is True
    
    def test_non_member_has_no_permission(self, company, external_user):
        """Usuário que não é membro não deve ter permissão"""
        # Arrange
        permission = IsCompanyMember()
        request = Mock()
        request.user = external_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is False
    
    def test_owner_is_member(self, company, owner):
        """Proprietário é automaticamente membro"""
        # Arrange
        permission = IsCompanyMember()
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is True


@pytest.mark.django_db
class TestIsCompanyAdminOrOwner:
    """Testes para permissão IsCompanyAdminOrOwner"""
    
    def test_company_owner_has_permission(self, company, owner):
        """Proprietário deve ter permissão"""
        # Arrange
        permission = IsCompanyAdminOrOwner()
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is True
    
    def test_company_admin_has_permission(self, company, admin_user):
        """Admin da empresa deve ter permissão"""
        # Arrange
        CompanyUser.objects.create(
            company=company,
            user=admin_user,
            role='admin'
        )
        permission = IsCompanyAdminOrOwner()
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is True
    
    def test_company_manager_has_no_permission(self, company, manager_user):
        """Manager não deve ter permissão para ações administrativas"""
        # Arrange
        CompanyUser.objects.create(
            company=company,
            user=manager_user,
            role='manager'
        )
        permission = IsCompanyAdminOrOwner()
        request = Mock()
        request.user = manager_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is False


@pytest.mark.django_db
class TestCompanyResourcePermission:
    """Testes para permissão CompanyResourcePermission"""
    
    def test_member_can_view_resource(self, company, admin_user, bank_account):
        """Membro pode visualizar recursos da empresa"""
        # Arrange
        CompanyUser.objects.create(
            company=company,
            user=admin_user,
            role='admin'
        )
        permission = CompanyResourcePermission()
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, bank_account)
        
        # Assert
        assert result is True
    
    def test_non_member_cannot_view_resource(self, company, external_user, bank_account):
        """Não-membro não pode visualizar recursos da empresa"""
        # Arrange
        permission = CompanyResourcePermission()
        request = Mock()
        request.user = external_user
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, bank_account)
        
        # Assert
        assert result is False


@pytest.mark.django_db
class TestIsCompanyActive:
    """Testes para permissão IsCompanyActive"""
    
    def test_active_company_has_permission(self, active_company, owner):
        """Empresa ativa deve permitir acesso"""
        # Arrange
        permission = IsCompanyActive()
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, active_company)
        
        # Assert
        assert result is True
    
    def test_inactive_company_has_no_permission(self, inactive_company, owner):
        """Empresa inativa não deve permitir acesso"""
        # Arrange
        permission = IsCompanyActive()
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, inactive_company)
        
        # Assert
        assert result is False


@pytest.mark.django_db
class TestHasSubscriptionFeature:
    """Testes para permissão HasSubscriptionFeature"""
    
    def test_subscription_with_feature_has_permission(self, company_with_subscription, owner):
        """Assinatura com feature deve permitir acesso"""
        # Arrange
        permission = HasSubscriptionFeature('advanced_reports')
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company_with_subscription)
        
        # Assert
        assert result is True
    
    def test_subscription_without_feature_has_no_permission(self, company_with_basic_subscription, owner):
        """Assinatura sem feature não deve permitir acesso"""
        # Arrange
        permission = HasSubscriptionFeature('advanced_reports')
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company_with_basic_subscription)
        
        # Assert
        assert result is False
    
    def test_company_without_subscription_has_no_permission(self, company, owner):
        """Empresa sem assinatura não deve permitir acesso"""
        # Arrange
        permission = HasSubscriptionFeature('advanced_reports')
        request = Mock()
        request.user = owner
        view = Mock()
        
        # Act
        result = permission.has_object_permission(request, view, company)
        
        # Assert
        assert result is False


# Fixtures
@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email='owner@example.com',
        password='TestPass123!',
        first_name='Owner',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@example.com',
        password='TestPass123!',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def manager_user(db):
    return User.objects.create_user(
        email='manager@example.com',
        password='TestPass123!',
        first_name='Manager',
        last_name='User'
    )


@pytest.fixture
def external_user(db):
    return User.objects.create_user(
        email='external@example.com',
        password='TestPass123!',
        first_name='External',
        last_name='User'
    )


@pytest.fixture
def company(owner):
    return Company.objects.create(
        name='Test Company',
        cnpj='11.222.333/0001-80',
        owner=owner
    )


@pytest.fixture
def active_company(owner):
    return Company.objects.create(
        name='Active Company',
        cnpj='11.222.333/0001-81',
        owner=owner,
        is_active=True
    )


@pytest.fixture
def inactive_company(owner):
    return Company.objects.create(
        name='Inactive Company',
        cnpj='11.222.333/0001-82',
        owner=owner,
        is_active=False
    )


@pytest.fixture
def starter_plan(db):
    return SubscriptionPlan.objects.create(
        name='Starter',
        slug='starter',
        price=29.90,
        features=['basic_reports']
    )


@pytest.fixture
def pro_plan(db):
    return SubscriptionPlan.objects.create(
        name='Pro',
        slug='pro',
        price=59.90,
        features=['basic_reports', 'advanced_reports']
    )


@pytest.fixture
def company_with_subscription(company, pro_plan):
    Subscription.objects.create(
        company=company,
        plan=pro_plan,
        status='active'
    )
    return company


@pytest.fixture
def company_with_basic_subscription(company, starter_plan):
    Subscription.objects.create(
        company=company,
        plan=starter_plan,
        status='active'
    )
    return company


@pytest.fixture
def bank_account(company):
    """Mock object representing a bank account resource"""
    mock_account = Mock()
    mock_account.company = company
    return mock_account