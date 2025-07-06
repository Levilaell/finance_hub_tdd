import pytest
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.companies.models import Company, CompanyUser

User = get_user_model()


@pytest.mark.django_db
class TestCompanyModel:
    """Testes para o modelo Company"""
    
    def test_create_company_with_owner(self, user):
        """Deve criar empresa com proprietário"""
        # Arrange
        company_data = {
            'name': 'Acme Corp',
            'legal_name': 'Acme Corporation LTDA',
            'cnpj': '11.222.333/0001-81',
            'owner': user
        }
        
        # Act
        company = Company.objects.create(**company_data)
        
        # Assert
        assert company.name == 'Acme Corp'
        assert company.legal_name == 'Acme Corporation LTDA'
        assert company.cnpj == '11.222.333/0001-81'
        assert company.owner == user
        assert isinstance(company.id, uuid.UUID)
        assert company.is_active is True
        
        # Verificar se o owner foi automaticamente adicionado como usuário da empresa
        assert CompanyUser.objects.filter(
            company=company, 
            user=user, 
            role='owner'
        ).exists()
    
    def test_create_company_without_owner_raises_error(self):
        """Deve levantar erro ao criar empresa sem proprietário"""
        # Act & Assert
        with pytest.raises(IntegrityError):
            Company.objects.create(
                name='Test Company',
                cnpj='11.222.333/0001-82'
            )
    
    def test_cnpj_uniqueness(self, user):
        """Deve garantir que CNPJ seja único"""
        # Arrange
        cnpj = '11.222.333/0001-83'
        Company.objects.create(
            name='First Company',
            cnpj=cnpj,
            owner=user
        )
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            Company.objects.create(
                name='Second Company',
                cnpj=cnpj,
                owner=user
            )
    
    def test_company_string_representation(self, user):
        """Deve retornar nome da empresa como representação string"""
        # Arrange
        company = Company.objects.create(
            name='Test Corp',
            cnpj='11.222.333/0001-84',
            owner=user
        )
        
        # Act & Assert
        assert str(company) == 'Test Corp'
    
    def test_company_slug_generation(self, user):
        """Deve gerar slug automaticamente baseado no nome"""
        # Arrange & Act
        company = Company.objects.create(
            name='My Amazing Company',
            cnpj='11.222.333/0001-85',
            owner=user
        )
        
        # Assert
        assert company.slug == 'my-amazing-company'
    
    def test_company_with_optional_fields(self, user):
        """Deve criar empresa com campos opcionais"""
        # Arrange & Act
        company = Company.objects.create(
            name='Full Company',
            legal_name='Full Company LTDA',
            cnpj='11.222.333/0001-86',
            company_type='LTDA',
            business_sector='Tecnologia',
            website='https://fullcompany.com',
            phone='(11) 99999-9999',
            email='contato@fullcompany.com',
            owner=user
        )
        
        # Assert
        assert company.company_type == 'LTDA'
        assert company.business_sector == 'Tecnologia'
        assert company.website == 'https://fullcompany.com'
        assert company.phone == '(11) 99999-9999'
        assert company.email == 'contato@fullcompany.com'


@pytest.mark.django_db
class TestCompanyUserModel:
    """Testes para o modelo CompanyUser"""
    
    def test_create_company_user_relationship(self, company):
        """Deve criar relacionamento usuário-empresa"""
        # Arrange
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='TestPass123!',
            first_name='New',
            last_name='User'
        )
        
        # Act
        company_user = CompanyUser.objects.create(
            company=company,
            user=new_user,
            role='admin'
        )
        
        # Assert
        assert company_user.company == company
        assert company_user.user == new_user
        assert company_user.role == 'admin'
        assert company_user.joined_at is not None
        assert company_user.is_active is True
    
    def test_company_user_unique_constraint(self, company):
        """Deve garantir que usuário não seja duplicado na mesma empresa"""
        # Arrange - criar novo usuário para evitar conflito com owner automático
        new_user = User.objects.create_user(
            email='duplicate@example.com',
            password='TestPass123!',
            first_name='Duplicate',
            last_name='User'
        )
        CompanyUser.objects.create(
            company=company,
            user=new_user,
            role='admin'
        )
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            CompanyUser.objects.create(
                company=company,
                user=new_user,
                role='manager'
            )
    
    def test_company_user_string_representation(self, company):
        """Deve retornar representação string correta"""
        # Arrange - criar novo usuário para evitar conflito com owner automático
        new_user = User.objects.create_user(
            email='stringtest@example.com',
            password='TestPass123!',
            first_name='String',
            last_name='Test'
        )
        company_user = CompanyUser.objects.create(
            company=company,
            user=new_user,
            role='admin'
        )
        
        # Act & Assert
        expected = f"{new_user.email} - {company.name} (admin)"
        assert str(company_user) == expected
    
    def test_user_can_belong_to_multiple_companies(self, user):
        """Usuário pode pertencer a múltiplas empresas"""
        # Arrange - criar empresas que automaticamente criam relacionamento owner
        company1 = Company.objects.create(
            name='Company 1',
            cnpj='11.111.111/0001-11',
            owner=user
        )
        company2 = Company.objects.create(
            name='Company 2',
            cnpj='22.222.222/0001-22',
            owner=user
        )
        
        # Act - o relacionamento owner é criado automaticamente pelo signal
        # Não precisamos criar manualmente
        
        # Assert
        assert user.company_memberships.count() == 2
        assert company1 in user.companies.all()
        assert company2 in user.companies.all()
        
        # Verificar que ambos relacionamentos são de owner
        company1_membership = user.company_memberships.get(company=company1)
        company2_membership = user.company_memberships.get(company=company2)
        assert company1_membership.role == 'owner'
        assert company2_membership.role == 'owner'


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def company(user):
    return Company.objects.create(
        name='Test Company',
        cnpj='11.222.333/0001-80',
        owner=user
    )