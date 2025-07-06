import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.companies.models import Company, CompanyUser, SubscriptionPlan, Subscription

User = get_user_model()


@pytest.mark.django_db
class TestCompanyViewSet:
    """Testes para CompanyViewSet"""
    
    def test_list_companies_authenticated_user(self, authenticated_client, user, company):
        """Usuário autenticado deve ver suas empresas"""
        # Arrange
        url = reverse('companies:company-list')
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(company.id)
        assert response.data['results'][0]['name'] == company.name
    
    def test_list_companies_unauthenticated_user(self, api_client):
        """Usuário não autenticado não deve ver empresas"""
        # Arrange
        url = reverse('companies:company-list')
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_company_valid_data(self, authenticated_client, user):
        """Deve criar empresa com dados válidos"""
        # Arrange
        url = reverse('companies:company-list')
        data = {
            'name': 'Nova Empresa',
            'legal_name': 'Nova Empresa LTDA',
            'cnpj': '11.222.333/0001-99',
            'company_type': 'LTDA',
            'business_sector': 'Tecnologia'
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Nova Empresa'
        assert response.data['cnpj'] == '11.222.333/0001-99'
        
        # Verificar se empresa foi criada no banco
        company = Company.objects.get(id=response.data['id'])
        assert company.owner == user
        assert company.slug == 'nova-empresa'
    
    def test_create_company_invalid_cnpj(self, authenticated_client):
        """Deve rejeitar CNPJ inválido"""
        # Arrange
        url = reverse('companies:company-list')
        data = {
            'name': 'Empresa Teste',
            'cnpj': '123.456.789-10'  # Formato inválido
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cnpj' in response.data
    
    def test_retrieve_company_owner(self, authenticated_client, company):
        """Proprietário deve ver detalhes da empresa"""
        # Arrange
        url = reverse('companies:company-detail', kwargs={'pk': company.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(company.id)
        assert response.data['name'] == company.name
    
    def test_retrieve_company_non_member(self, api_client, external_user, company):
        """Não-membro não deve ver detalhes da empresa"""
        # Arrange
        api_client.force_authenticate(user=external_user)
        url = reverse('companies:company-detail', kwargs={'pk': company.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_company_owner(self, authenticated_client, company):
        """Proprietário deve poder atualizar empresa"""
        # Arrange
        url = reverse('companies:company-detail', kwargs={'pk': company.id})
        data = {
            'name': 'Empresa Atualizada',
            'business_sector': 'Financeiro'
        }
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Empresa Atualizada'
        assert response.data['business_sector'] == 'Financeiro'
    
    def test_update_company_non_owner(self, api_client, admin_user, company):
        """Não-proprietário não deve poder atualizar empresa"""
        # Arrange
        CompanyUser.objects.create(company=company, user=admin_user, role='admin')
        api_client.force_authenticate(user=admin_user)
        url = reverse('companies:company-detail', kwargs={'pk': company.id})
        data = {'name': 'Tentativa de Atualização'}
        
        # Act
        response = api_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_company_owner(self, authenticated_client, company):
        """Proprietário deve poder deletar empresa"""
        # Arrange
        url = reverse('companies:company-detail', kwargs={'pk': company.id})
        
        # Act
        response = authenticated_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Company.objects.filter(id=company.id).exists()


@pytest.mark.django_db
class TestCompanyUserViewSet:
    """Testes para CompanyUserViewSet"""
    
    def test_list_company_members(self, authenticated_client, company, admin_user):
        """Deve listar membros da empresa"""
        # Arrange
        CompanyUser.objects.create(company=company, user=admin_user, role='admin')
        url = reverse('companies:company-members-list', kwargs={'company_pk': company.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # owner + admin
    
    def test_invite_user_to_company(self, authenticated_client, company, admin_user):
        """Proprietário deve poder convidar usuários"""
        # Arrange
        url = reverse('companies:company-members-list', kwargs={'company_pk': company.id})
        data = {
            'email': admin_user.email,
            'role': 'admin'
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['role'] == 'admin'
        assert response.data['user']['email'] == admin_user.email
    
    def test_invite_nonexistent_user(self, authenticated_client, company):
        """Deve rejeitar convite para usuário inexistente"""
        # Arrange
        url = reverse('companies:company-members-list', kwargs={'company_pk': company.id})
        data = {
            'email': 'naoexiste@example.com',
            'role': 'admin'
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_remove_member_from_company(self, authenticated_client, company, admin_user):
        """Proprietário deve poder remover membros"""
        # Arrange
        company_user = CompanyUser.objects.create(
            company=company, user=admin_user, role='admin'
        )
        url = reverse(
            'companies:company-members-detail',
            kwargs={'company_pk': company.id, 'pk': company_user.id}
        )
        
        # Act
        response = authenticated_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CompanyUser.objects.filter(id=company_user.id).exists()


@pytest.mark.django_db
class TestSubscriptionPlanViewSet:
    """Testes para SubscriptionPlanViewSet"""
    
    def test_list_subscription_plans(self, api_client, starter_plan, pro_plan):
        """Deve listar planos disponíveis (público)"""
        # Arrange
        url = reverse('companies:subscriptionplan-list')
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_retrieve_subscription_plan(self, api_client, starter_plan):
        """Deve mostrar detalhes do plano (público)"""
        # Arrange
        url = reverse('companies:subscriptionplan-detail', kwargs={'pk': starter_plan.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == starter_plan.name
        assert response.data['price'] == str(starter_plan.price)


@pytest.mark.django_db
class TestSubscriptionViewSet:
    """Testes para SubscriptionViewSet"""
    
    def test_create_subscription(self, authenticated_client, company, starter_plan):
        """Deve criar assinatura para empresa"""
        # Arrange
        url = reverse('companies:subscription-list')
        data = {
            'company_id': str(company.id),
            'plan_id': str(starter_plan.id),
            'status': 'trial',
            'trial_days': 14
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'trial'
        assert response.data['trial_days'] == 14
    
    def test_retrieve_company_subscription(self, authenticated_client, subscription):
        """Deve mostrar assinatura da empresa"""
        # Arrange
        url = reverse('companies:subscription-detail', kwargs={'pk': subscription.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(subscription.id)
        assert response.data['status'] == subscription.status
    
    def test_cancel_subscription(self, authenticated_client, subscription):
        """Proprietário deve poder cancelar assinatura"""
        # Arrange
        url = reverse('companies:subscription-detail', kwargs={'pk': subscription.id})
        data = {'status': 'cancelled'}
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'


# Fixtures
@pytest.fixture
def api_client():
    return APIClient()


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
def external_user(db):
    return User.objects.create_user(
        email='external@example.com',
        password='TestPass123!',
        first_name='External',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


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
def subscription(company, starter_plan):
    return Subscription.objects.create(
        company=company,
        plan=starter_plan,
        status='active'
    )