import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager que usa email como username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário regular"""
        if not email:
            raise ValueError("Email é obrigatório")
        if not password:
            raise ValueError("Senha é obrigatória")
            
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Modelo de usuário customizado que usa email como username"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo')
    language = models.CharField(max_length=10, default='pt-BR')
    
    # Campos de 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Campos de verificação de email
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Campos de reset de senha
    password_reset_token = models.CharField(max_length=64, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Campos de auditoria
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Campos de pagamento
    customer_id = models.CharField(max_length=50, blank=True)
    payment_gateway = models.CharField(max_length=20, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """Garante que username sempre seja igual ao email"""
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)
