from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        """Validar se as senhas conferem"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não conferem.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Criar novo usuário"""
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuários"""
    
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """Validar credenciais de login"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Email ou senha incorretos.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Conta desativada.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Email e senha são obrigatórios.',
                code='authorization'
            )


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'phone', 'avatar', 'date_of_birth', 'timezone', 
            'language', 'email_verified', 'two_factor_enabled',
            'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'email', 'email_verified', 'two_factor_enabled',
            'date_joined', 'last_login'
        ]