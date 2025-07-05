import pytest
import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def user(user_data):
    return User.objects.create_user(**user_data)


@pytest.fixture
def authenticated_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.mark.django_db
class TestUserRegistrationAPI:
    """Testes para o endpoint de registro de usuário"""
    
    def test_user_registration_success(self, api_client):
        """Deve registrar novo usuário e retornar tokens JWT"""
        # Arrange
        url = reverse('auth:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']
        assert User.objects.filter(email=data['email']).exists()
        
        # Verificar que usuário foi criado corretamente
        user = User.objects.get(email=data['email'])
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.email_verified is False
    
    def test_user_registration_password_mismatch(self, api_client):
        """Deve retornar erro quando senhas não conferem"""
        # Arrange
        url = reverse('auth:register')
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_user_registration_duplicate_email(self, api_client, user):
        """Deve retornar erro quando email já existe"""
        # Arrange
        url = reverse('auth:register')
        data = {
            'email': user.email,
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestUserLoginAPI:
    """Testes para o endpoint de login"""
    
    def test_login_with_valid_credentials(self, api_client, user, user_data):
        """Deve autenticar com credenciais válidas"""
        # Arrange
        url = reverse('auth:login')
        data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == user.email
    
    def test_login_with_invalid_credentials(self, api_client, user):
        """Deve retornar erro com credenciais inválidas"""
        # Arrange
        url = reverse('auth:login')
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_with_nonexistent_email(self, api_client):
        """Deve retornar erro com email inexistente"""
        # Arrange
        url = reverse('auth:login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefreshAPI:
    """Testes para o endpoint de refresh de token"""
    
    def test_token_refresh_success(self, api_client, user):
        """Deve renovar token de acesso com refresh token válido"""
        # Arrange
        refresh = RefreshToken.for_user(user)
        url = reverse('auth:token-refresh')
        data = {'refresh': str(refresh)}
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_token_refresh_invalid_token(self, api_client):
        """Deve retornar erro com refresh token inválido"""
        # Arrange
        url = reverse('auth:token-refresh')
        data = {'refresh': 'invalid_token'}
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfileAPI:
    """Testes para o endpoint de perfil do usuário"""
    
    def test_get_user_profile_authenticated(self, authenticated_client, user):
        """Deve retornar perfil do usuário autenticado"""
        # Arrange
        url = reverse('auth:profile')
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name
    
    def test_get_user_profile_unauthenticated(self, api_client):
        """Deve retornar erro para usuário não autenticado"""
        # Arrange
        url = reverse('auth:profile')
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_user_profile(self, authenticated_client, user):
        """Deve atualizar perfil do usuário"""
        # Arrange
        url = reverse('auth:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+5511999999999'
        }
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == data['first_name']
        assert response.data['last_name'] == data['last_name']
        assert response.data['phone'] == data['phone']
        
        # Verificar no banco
        user.refresh_from_db()
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.phone == data['phone']