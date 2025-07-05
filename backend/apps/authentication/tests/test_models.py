import pytest
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Testes para o modelo User customizado"""
    
    def test_create_user_with_email(self):
        """Deve criar usuário usando email como username"""
        # Arrange
        email = "test@example.com"
        password = "TestPass123!"
        first_name = "Test"
        last_name = "User"
        
        # Act
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Assert
        assert user.email == email
        assert user.username == email
        assert user.check_password(password)
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert isinstance(user.id, uuid.UUID)
    
    def test_create_user_without_email_raises_error(self):
        """Deve levantar erro ao criar usuário sem email"""
        # Act & Assert
        with pytest.raises(ValueError, match="Email é obrigatório"):
            User.objects.create_user(
                email="",
                password="TestPass123!",
                first_name="Test",
                last_name="User"
            )
    
    def test_create_user_without_password_raises_error(self):
        """Deve levantar erro ao criar usuário sem senha"""
        # Act & Assert
        with pytest.raises(ValueError, match="Senha é obrigatória"):
            User.objects.create_user(
                email="test@example.com",
                password="",
                first_name="Test",
                last_name="User"
            )
    
    def test_create_superuser(self):
        """Deve criar superusuário com permissões admin"""
        # Arrange
        email = "admin@example.com"
        password = "AdminPass123!"
        
        # Act
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Admin",
            last_name="User"
        )
        
        # Assert
        assert user.email == email
        assert user.username == email
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
    
    def test_email_uniqueness(self):
        """Deve garantir que email seja único"""
        # Arrange
        email = "unique@example.com"
        User.objects.create_user(
            email=email,
            password="TestPass123!",
            first_name="First",
            last_name="User"
        )
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email=email,
                password="TestPass456!",
                first_name="Second",
                last_name="User"
            )
    
    def test_user_full_name_property(self):
        """Deve retornar nome completo do usuário"""
        # Arrange
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe"
        )
        
        # Act
        full_name = user.get_full_name()
        
        # Assert
        assert full_name == "John Doe"
    
    def test_user_string_representation(self):
        """Deve retornar email como representação string"""
        # Arrange
        email = "test@example.com"
        user = User.objects.create_user(
            email=email,
            password="TestPass123!",
            first_name="Test",
            last_name="User"
        )
        
        # Act & Assert
        assert str(user) == email