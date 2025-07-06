import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Company(models.Model):
    """Modelo para empresas do sistema"""
    
    COMPANY_TYPE_CHOICES = [
        ('MEI', 'Microempreendedor Individual'),
        ('ME', 'Microempresa'),
        ('EPP', 'Empresa de Pequeno Porte'),
        ('LTDA', 'Sociedade Limitada'),
        ('SA', 'Sociedade Anônima'),
        ('EIRELI', 'Empresa Individual de Responsabilidade Limitada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nome da Empresa')
    legal_name = models.CharField(max_length=200, blank=True, verbose_name='Razão Social')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, verbose_name='CNPJ')
    company_type = models.CharField(
        max_length=10, 
        choices=COMPANY_TYPE_CHOICES, 
        blank=True,
        verbose_name='Tipo de Empresa'
    )
    business_sector = models.CharField(max_length=100, blank=True, verbose_name='Setor')
    
    # Dados de contato
    website = models.URLField(blank=True, verbose_name='Website')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='Email')
    
    # Relacionamentos
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_companies',
        verbose_name='Proprietário'
    )
    users = models.ManyToManyField(
        User,
        through='CompanyUser',
        related_name='companies',
        verbose_name='Usuários'
    )
    
    # Controle
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.legal_name:
            self.legal_name = self.name
        super().save(*args, **kwargs)


class CompanyUser(models.Model):
    """Modelo para relacionamento usuário-empresa com papéis"""
    
    ROLE_CHOICES = [
        ('owner', 'Proprietário'),
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('accountant', 'Contador'),
        ('viewer', 'Visualizador'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name='Empresa'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name='Usuário'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Papel'
    )
    
    # Controle
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Ingressou em')
    
    class Meta:
        verbose_name = 'Usuário da Empresa'
        verbose_name_plural = 'Usuários das Empresas'
        unique_together = ['company', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.company.name} ({self.role})"


class SubscriptionPlan(models.Model):
    """Modelo para planos de assinatura"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Nome do Plano')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Descrição')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço'
    )
    
    # Limites do plano
    max_companies = models.PositiveIntegerField(
        default=1, 
        verbose_name='Máximo de Empresas'
    )
    max_bank_accounts = models.PositiveIntegerField(
        default=1,
        verbose_name='Máximo de Contas Bancárias'
    )
    max_transactions_per_month = models.PositiveIntegerField(
        default=100,
        verbose_name='Máximo de Transações por Mês'
    )
    
    # Features como JSON field
    features = models.JSONField(default=list, verbose_name='Funcionalidades')
    
    # Controle
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Plano de Assinatura'
        verbose_name_plural = 'Planos de Assinatura'
        ordering = ['price']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """Modelo para assinaturas das empresas"""
    
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Ativa'),
        ('past_due', 'Vencida'),
        ('cancelled', 'Cancelada'),
        ('suspended', 'Suspensa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Empresa'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Plano'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
        verbose_name='Status'
    )
    
    # Datas
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Iniciada em')
    trial_days = models.PositiveIntegerField(default=0, verbose_name='Dias de Trial')
    next_billing_date = models.DateField(null=True, blank=True, verbose_name='Próxima Cobrança')
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='Cancelada em')
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return self.status in ['trial', 'active']
    
    def clean(self):
        # Validar que empresa não tenha múltiplas assinaturas ativas
        if self.status in ['trial', 'active']:
            existing = Subscription.objects.filter(
                company=self.company,
                status__in=['trial', 'active']
            ).exclude(id=self.id)
            
            if existing.exists():
                raise ValidationError(
                    'Empresa já possui uma assinatura ativa.'
                )


@receiver(post_save, sender=Company)
def create_owner_company_user(sender, instance, created, **kwargs):
    """Cria automaticamente o relacionamento owner quando empresa é criada"""
    if created:
        CompanyUser.objects.create(
            company=instance,
            user=instance.owner,
            role='owner'
        )
