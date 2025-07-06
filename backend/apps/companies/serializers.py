import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Company, CompanyUser, SubscriptionPlan, Subscription

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para dados do usuário"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer para planos de assinatura"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'max_companies', 'max_bank_accounts', 'max_transactions_per_month',
            'features', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinaturas"""
    
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True, source='plan')
    company_id = serializers.UUIDField(write_only=True, source='company')
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'company_id', 'plan', 'plan_id', 'status',
            'started_at', 'trial_days', 'next_billing_date',
            'cancelled_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validar que empresa não tenha múltiplas assinaturas ativas"""
        # Converter company_id para objeto Company se necessário
        company_id = attrs.get('company')
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                attrs['company'] = company
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'company_id': 'Empresa não encontrada.'
                })
        else:
            company = attrs.get('company')
        
        # Converter plan_id para objeto SubscriptionPlan se necessário
        plan_id = attrs.get('plan')
        if plan_id:
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id)
                attrs['plan'] = plan
            except SubscriptionPlan.DoesNotExist:
                raise serializers.ValidationError({
                    'plan_id': 'Plano não encontrado.'
                })
        
        status = attrs.get('status', 'trial')
        
        if status in ['trial', 'active']:
            # Verificar se já existe assinatura ativa para esta empresa
            existing = Subscription.objects.filter(
                company=company,
                status__in=['trial', 'active']
            )
            
            # Se estamos editando, excluir a própria instância
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'company_id': 'Empresa já possui uma assinatura ativa.'
                })
        
        return attrs


class CompanyUserSerializer(serializers.ModelSerializer):
    """Serializer para relacionamento usuário-empresa"""
    
    user = UserBasicSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    company_id = serializers.UUIDField(write_only=True, source='company', required=False)
    
    class Meta:
        model = CompanyUser
        fields = [
            'id', 'company_id', 'user', 'email', 'role',
            'is_active', 'joined_at'
        ]
        read_only_fields = ['id', 'user', 'joined_at']
    
    def validate_email(self, value):
        """Validar que o usuário existe"""
        try:
            user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Usuário com este email não encontrado.'
            )
    
    def create(self, validated_data):
        """Criar relacionamento usuário-empresa"""
        email = validated_data.pop('email')
        user = User.objects.get(email=email)
        
        # Converter company_id para objeto Company se fornecido
        company_id = validated_data.pop('company', None)
        if company_id:
            company = Company.objects.get(id=company_id)
            validated_data['company'] = company
        
        validated_data['user'] = user
        return super().create(validated_data)


class CompanyUserCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para criação de convites via view nested"""
    
    user = UserBasicSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = CompanyUser
        fields = [
            'id', 'user', 'email', 'role',
            'is_active', 'joined_at'
        ]
        read_only_fields = ['id', 'user', 'joined_at']
    
    def validate_email(self, value):
        """Validar que o usuário existe"""
        try:
            user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Usuário com este email não encontrado.'
            )
    
    def create(self, validated_data):
        """Criar relacionamento usuário-empresa"""
        email = validated_data.pop('email')
        user = User.objects.get(email=email)
        validated_data['user'] = user
        return super().create(validated_data)


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para leitura de empresas"""
    
    subscription = SubscriptionSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'legal_name', 'slug', 'cnpj',
            'company_type', 'business_sector', 'website',
            'phone', 'email', 'is_active', 'subscription',
            'members_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'subscription', 'members_count',
            'created_at', 'updated_at'
        ]
    
    def get_members_count(self, obj):
        """Retornar número de membros da empresa"""
        return obj.company_memberships.filter(is_active=True).count()


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de empresas"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'legal_name', 'cnpj', 'company_type',
            'business_sector', 'website', 'phone', 'email'
        ]
    
    def validate_cnpj(self, value):
        """Validar formato do CNPJ"""
        # Remover caracteres não numéricos
        cnpj_digits = re.sub(r'[^\d]', '', value)
        
        # Verificar se tem 14 dígitos
        if len(cnpj_digits) != 14:
            raise serializers.ValidationError(
                'CNPJ deve conter 14 dígitos.'
            )
        
        # Verificar se não é uma sequência de números iguais
        if len(set(cnpj_digits)) == 1:
            raise serializers.ValidationError(
                'CNPJ inválido.'
            )
        
        return value
    
    def create(self, validated_data):
        """Criar empresa com owner definido pelo usuário da request"""
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)