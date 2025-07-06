import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from apps.companies.models import Company, CompanyUser, SubscriptionPlan, Subscription
from apps.companies.serializers import (
    CompanySerializer,
    CompanyCreateSerializer,
    CompanyUserSerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestCompanySerializer:
    """Testes para CompanySerializer"""
    
    def test_serialize_company(self, company):
        """Deve serializar empresa corretamente"""
        # Arrange & Act
        serializer = CompanySerializer(company)
        data = serializer.data
        
        # Assert
        assert data['id'] == str(company.id)
        assert data['name'] == company.name
        assert data['legal_name'] == company.legal_name
        assert data['cnpj'] == company.cnpj
        assert data['slug'] == company.slug
        assert data['is_active'] == company.is_active
        assert 'created_at' in data
        assert 'updated_at' in data
        # Campos sensíveis não devem estar expostos
        assert 'owner' not in data
    
    def test_serialize_company_with_subscription(self, company_with_subscription):
        """Deve incluir dados da assinatura quando presente"""
        # Arrange & Act
        serializer = CompanySerializer(company_with_subscription)
        data = serializer.data
        
        # Assert
        assert 'subscription' in data
        assert data['subscription']['status'] == 'active'
        assert data['subscription']['plan']['name'] == 'Pro'
    
    def test_serialize_company_without_subscription(self, company):
        """Deve mostrar subscription como null quando não há assinatura"""
        # Arrange & Act
        serializer = CompanySerializer(company)
        data = serializer.data
        
        # Assert
        assert data['subscription'] is None


@pytest.mark.django_db
class TestCompanyCreateSerializer:
    """Testes para CompanyCreateSerializer"""
    
    def test_create_company_valid_data(self, user):
        """Deve criar empresa com dados válidos"""
        # Arrange
        data = {
            'name': 'Nova Empresa',
            'legal_name': 'Nova Empresa LTDA',
            'cnpj': '11.222.333/0001-99',
            'company_type': 'LTDA',
            'business_sector': 'Tecnologia'
        }
        request = type('obj', (object,), {'user': user})
        serializer = CompanyCreateSerializer(data=data, context={'request': request})
        
        # Act
        assert serializer.is_valid()
        company = serializer.save()
        
        # Assert
        assert company.name == 'Nova Empresa'
        assert company.cnpj == '11.222.333/0001-99'
        assert company.owner == user
        assert company.slug == 'nova-empresa'
        # Verificar se o owner foi adicionado automaticamente como usuário
        assert CompanyUser.objects.filter(
            company=company, 
            user=user, 
            role='owner'
        ).exists()
    
    def test_create_company_duplicate_cnpj(self, user, company):
        """Deve rejeitar CNPJ duplicado"""
        # Arrange
        data = {
            'name': 'Outra Empresa',
            'cnpj': company.cnpj  # CNPJ já existe
        }
        serializer = CompanyCreateSerializer(data=data)
        
        # Act & Assert
        assert not serializer.is_valid()
        assert 'cnpj' in serializer.errors
    
    def test_create_company_invalid_cnpj_format(self, user):
        """Deve validar formato do CNPJ"""
        # Arrange
        data = {
            'name': 'Empresa Teste',
            'cnpj': '123.456.789-10'  # Formato inválido
        }
        serializer = CompanyCreateSerializer(data=data)
        
        # Act & Assert
        assert not serializer.is_valid()
        assert 'cnpj' in serializer.errors


@pytest.mark.django_db
class TestCompanyUserSerializer:
    """Testes para CompanyUserSerializer"""
    
    def test_serialize_company_user(self, company_user):
        """Deve serializar relacionamento usuário-empresa"""
        # Arrange & Act
        serializer = CompanyUserSerializer(company_user)
        data = serializer.data
        
        # Assert
        assert data['id'] == str(company_user.id)
        assert data['role'] == company_user.role
        assert data['is_active'] == company_user.is_active
        assert 'joined_at' in data
        assert 'user' in data
        assert data['user']['email'] == company_user.user.email
        assert data['user']['first_name'] == company_user.user.first_name
    
    def test_create_company_user_invitation(self, company, admin_user):
        """Deve criar convite para usuário existente"""
        # Arrange
        data = {
            'company_id': str(company.id),
            'email': admin_user.email,
            'role': 'admin'
        }
        serializer = CompanyUserSerializer(data=data)
        
        # Act
        assert serializer.is_valid()
        company_user = serializer.save()
        
        # Assert
        assert company_user.company == company
        assert company_user.user == admin_user
        assert company_user.role == 'admin'
    
    def test_create_company_user_invalid_email(self, company):
        """Deve rejeitar email não existente"""
        # Arrange
        data = {
            'company_id': str(company.id),
            'email': 'naoexiste@example.com',
            'role': 'admin'
        }
        serializer = CompanyUserSerializer(data=data)
        
        # Act & Assert
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestSubscriptionPlanSerializer:
    """Testes para SubscriptionPlanSerializer"""
    
    def test_serialize_subscription_plan(self, pro_plan):
        """Deve serializar plano de assinatura"""
        # Arrange & Act
        serializer = SubscriptionPlanSerializer(pro_plan)
        data = serializer.data
        
        # Assert
        assert data['id'] == str(pro_plan.id)
        assert data['name'] == pro_plan.name
        assert data['slug'] == pro_plan.slug
        assert data['price'] == str(pro_plan.price)
        assert data['max_companies'] == pro_plan.max_companies
        assert data['features'] == pro_plan.features
        assert data['is_active'] == pro_plan.is_active


@pytest.mark.django_db
class TestSubscriptionSerializer:
    """Testes para SubscriptionSerializer"""
    
    def test_serialize_subscription(self, subscription):
        """Deve serializar assinatura"""
        # Arrange & Act
        serializer = SubscriptionSerializer(subscription)
        data = serializer.data
        
        # Assert
        assert data['id'] == str(subscription.id)
        assert data['status'] == subscription.status
        assert data['trial_days'] == subscription.trial_days
        assert 'started_at' in data
        assert 'plan' in data
        assert data['plan']['name'] == subscription.plan.name
    
    def test_create_subscription(self, company, pro_plan):
        """Deve criar nova assinatura"""
        # Arrange
        data = {
            'company_id': str(company.id),
            'plan_id': str(pro_plan.id),
            'status': 'trial',
            'trial_days': 14
        }
        serializer = SubscriptionSerializer(data=data)
        
        # Act
        assert serializer.is_valid()
        subscription = serializer.save()
        
        # Assert
        assert subscription.company == company
        assert subscription.plan == pro_plan
        assert subscription.status == 'trial'
        assert subscription.trial_days == 14
    
    def test_prevent_multiple_active_subscriptions(self, company_with_subscription, starter_plan):
        """Deve prevenir múltiplas assinaturas ativas"""
        # Arrange
        data = {
            'company_id': str(company_with_subscription.id),
            'plan_id': str(starter_plan.id),
            'status': 'active'
        }
        serializer = SubscriptionSerializer(data=data)
        
        # Act & Assert
        assert not serializer.is_valid()
        assert 'company_id' in serializer.errors


# Fixtures
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
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
def company(user):
    return Company.objects.create(
        name='Test Company',
        legal_name='Test Company LTDA',
        cnpj='11.222.333/0001-80',
        company_type='LTDA',
        business_sector='Tecnologia',
        owner=user
    )


@pytest.fixture
def company_user(company, admin_user):
    return CompanyUser.objects.create(
        company=company,
        user=admin_user,
        role='admin'
    )


@pytest.fixture
def starter_plan(db):
    return SubscriptionPlan.objects.create(
        name='Starter',
        slug='starter',
        price=Decimal('29.90'),
        max_companies=1,
        features=['basic_reports']
    )


@pytest.fixture
def pro_plan(db):
    return SubscriptionPlan.objects.create(
        name='Pro',
        slug='pro',
        price=Decimal('59.90'),
        max_companies=3,
        features=['basic_reports', 'advanced_reports']
    )


@pytest.fixture
def subscription(company, pro_plan):
    return Subscription.objects.create(
        company=company,
        plan=pro_plan,
        status='active'
    )


@pytest.fixture
def company_with_subscription(company, pro_plan):
    Subscription.objects.create(
        company=company,
        plan=pro_plan,
        status='active'
    )
    return company