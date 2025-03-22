from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserPermission, AuthToken
from django.utils import timezone
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'bio', 'phone_number', 'address')
        read_only_fields = ('id',)

class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = ('id', 'user', 'permission_name', 'permission_description', 'created_at')
        read_only_fields = ('id', 'created_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    token = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Nom d\'utilisateur ou mot de passe incorrect.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte est désactivé.')
        else:
            raise serializers.ValidationError('Vous devez fournir un nom d\'utilisateur et un mot de passe.')
        
        # Génération d'un token
        token_obj = AuthToken.generate_token(user)
        
        attrs['user'] = user
        attrs['token'] = token_obj.token
        attrs['expires_at'] = token_obj.expires_at
        
        return attrs

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ('token', 'created_at', 'expires_at')
        read_only_fields = ('token', 'created_at', 'expires_at') 