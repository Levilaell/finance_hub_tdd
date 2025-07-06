import pytest
import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.companies.models import Company, SubscriptionPlan, Subscription

User = get_user_model()


@pytest.mark.django_db
class TestSubscriptionPlanModel:
    """Testes para o modelo SubscriptionPlan"""
    
    def test_create_subscription_plan(self):
        """Deve criar plano de assinatura"""
        # Arrange & Act
        plan = SubscriptionPlan.objects.create(
            name='Starter',
            slug='starter',
            description='Plano básico para pequenas empresas',
            price=Decimal('29.90'),
            max_companies=1,
            max_bank_accounts=2,
            max_transactions_per_month=1000,
            features=['basic_reports', 'bank_integration']
        )
        
        # Assert
        assert plan.name == 'Starter'
        assert plan.slug == 'starter'
        assert plan.price == Decimal('29.90')
        assert plan.max_companies == 1
        assert plan.max_bank_accounts == 2
        assert plan.max_transactions_per_month == 1000
        assert plan.features == ['basic_reports', 'bank_integration']
        assert isinstance(plan.id, uuid.UUID)
        assert plan.is_active is True
    
    def test_subscription_plan_string_representation(self):
        """Deve retornar nome do plano como representação string"""
        # Arrange & Act
        plan = SubscriptionPlan.objects.create(
            name='Pro Plan',
            price=Decimal('59.90')
        )
        
        # Assert
        assert str(plan) == 'Pro Plan'
    
    def test_subscription_plan_slug_uniqueness(self):
        """Deve garantir que slug seja único"""
        # Arrange
        SubscriptionPlan.objects.create(
            name='Plan 1',
            slug='unique-plan',
            price=Decimal('29.90')
        )
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            SubscriptionPlan.objects.create(
                name='Plan 2',
                slug='unique-plan',
                price=Decimal('49.90')
            )
    
    def test_subscription_plan_auto_slug_generation(self):
        """Deve gerar slug automaticamente baseado no nome"""
        # Arrange & Act
        plan = SubscriptionPlan.objects.create(
            name='Premium Enterprise Plan',
            price=Decimal('199.90')
        )
        
        # Assert
        assert plan.slug == 'premium-enterprise-plan'
    
    def test_subscription_plan_price_validation(self):
        """Deve validar que preço seja positivo"""
        # Act & Assert
        with pytest.raises(ValidationError):
            plan = SubscriptionPlan(
                name='Invalid Plan',
                price=-10.00
            )
            plan.full_clean()


@pytest.mark.django_db
class TestSubscriptionModel:
    """Testes para o modelo Subscription"""
    
    def test_create_subscription(self, company, starter_plan):
        """Deve criar assinatura para empresa"""
        # Arrange & Act
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='active'
        )
        
        # Assert
        assert subscription.company == company
        assert subscription.plan == starter_plan
        assert subscription.status == 'active'
        assert isinstance(subscription.id, uuid.UUID)
        assert subscription.started_at is not None
        assert subscription.is_active is True
    
    def test_subscription_string_representation(self, company, starter_plan):
        """Deve retornar representação string correta"""
        # Arrange & Act
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='active'
        )
        
        # Assert
        expected = f"{company.name} - {starter_plan.name} (active)"
        assert str(subscription) == expected
    
    def test_company_can_have_only_one_active_subscription(self, company, starter_plan, pro_plan):
        """Empresa pode ter apenas uma assinatura ativa"""
        # Arrange
        Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='active'
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            subscription = Subscription(
                company=company,
                plan=pro_plan,
                status='active'
            )
            subscription.full_clean()
    
    def test_subscription_status_choices(self, company, starter_plan):
        """Deve aceitar apenas status válidos"""
        # Arrange & Act
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='trial'
        )
        
        # Assert
        assert subscription.status == 'trial'
        
        # Test invalid status
        with pytest.raises(ValidationError):
            subscription.status = 'invalid_status'
            subscription.full_clean()
    
    def test_subscription_cancellation(self, company, starter_plan):
        """Deve permitir cancelamento de assinatura"""
        # Arrange
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='active'
        )
        
        # Act
        subscription.status = 'cancelled'
        subscription.save()
        
        # Assert
        assert subscription.status == 'cancelled'
        assert subscription.is_active is False
    
    def test_subscription_trial_period(self, company, starter_plan):
        """Deve suportar período de trial"""
        # Arrange & Act
        subscription = Subscription.objects.create(
            company=company,
            plan=starter_plan,
            status='trial',
            trial_days=14
        )
        
        # Assert
        assert subscription.trial_days == 14
        assert subscription.status == 'trial'


@pytest.fixture
def starter_plan(db):
    return SubscriptionPlan.objects.create(
        name='Starter',
        slug='starter',
        description='Plano básico',
        price=Decimal('29.90'),
        max_companies=1,
        max_bank_accounts=2,
        max_transactions_per_month=1000,
        features=['basic_reports']
    )


@pytest.fixture
def pro_plan(db):
    return SubscriptionPlan.objects.create(
        name='Pro',
        slug='pro',
        description='Plano profissional',
        price=Decimal('59.90'),
        max_companies=3,
        max_bank_accounts=5,
        max_transactions_per_month=5000,
        features=['advanced_reports', 'api_access']
    )


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