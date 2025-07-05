import pytest
from django.contrib.auth import get_user_model
from apps.authentication.serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    UserLoginSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Testes para o serializer de registro de usuário"""
    
    def test_valid_registration_data(self):
        """Deve validar dados corretos de registro"""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        serializer = UserRegistrationSerializer(data=data)
        
        # Assert
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == data['email']
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.check_password(data['password'])
    
    def test_password_mismatch_validation(self):
        """Deve invalidar quando senhas não conferem"""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        serializer = UserRegistrationSerializer(data=data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors
    
    def test_weak_password_validation(self):
        """Deve invalidar senhas fracas"""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        serializer = UserRegistrationSerializer(data=data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_invalid_email_format(self):
        """Deve invalidar formato de email inválido"""
        # Arrange
        data = {
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        serializer = UserRegistrationSerializer(data=data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestUserLoginSerializer:
    """Testes para o serializer de login"""
    
    def test_valid_login_credentials(self):
        """Deve validar credenciais corretas"""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        # Act
        serializer = UserLoginSerializer(data=data)
        
        # Assert
        assert serializer.is_valid()
        validated_data = serializer.validated_data
        assert validated_data['user'] == user
    
    def test_invalid_login_credentials(self):
        """Deve invalidar credenciais incorretas"""
        # Arrange
        User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        # Act
        serializer = UserLoginSerializer(data=data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
    
    def test_nonexistent_user_login(self):
        """Deve invalidar login de usuário inexistente"""
        # Arrange
        data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        # Act
        serializer = UserLoginSerializer(data=data)
        
        # Assert
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
class TestUserSerializer:
    """Testes para o serializer de usuário"""
    
    def test_user_serialization(self):
        """Deve serializar dados do usuário corretamente"""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            phone='+5511999999999'
        )
        
        # Act
        serializer = UserSerializer(user)
        
        # Assert
        data = serializer.data
        assert data['id'] == str(user.id)
        assert data['email'] == user.email
        assert data['first_name'] == user.first_name
        assert data['last_name'] == user.last_name
        assert data['phone'] == user.phone
        assert 'password' not in data  # Senha não deve ser exposta
    
    def test_user_update(self):
        """Deve atualizar dados do usuário"""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Old',
            last_name='Name'
        )
        data = {
            'first_name': 'New',
            'last_name': 'Name',
            'phone': '+5511999999999'
        }
        
        # Act
        serializer = UserSerializer(user, data=data, partial=True)
        
        # Assert
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.first_name == data['first_name']
        assert updated_user.last_name == data['last_name']
        assert updated_user.phone == data['phone']
    
    def test_readonly_fields(self):
        """Deve proteger campos readonly"""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        original_email = user.email
        original_id = user.id
        
        data = {
            'id': 'new-id',
            'email': 'newemail@example.com',
            'first_name': 'Updated'
        }
        
        # Act
        serializer = UserSerializer(user, data=data, partial=True)
        
        # Assert
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert str(updated_user.id) == str(original_id)  # ID não deve mudar
        assert updated_user.email == original_email  # Email não deve mudar
        assert updated_user.first_name == data['first_name']  # Apenas este deve mudar