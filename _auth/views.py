from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, UserPermission, AuthToken
from .serializers import (
    UserSerializer, 
    UserPermissionSerializer, 
    UserRegistrationSerializer,
    LoginSerializer,
    TokenSerializer
)
from .authentication import TokenAuthentication

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

class UserPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserPermission.objects.all()
        return UserPermission.objects.filter(user=self.request.user)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Génère un token pour l'utilisateur nouvellement créé
            token = AuthToken.generate_token(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.token,
                'expires_at': token.expires_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'user': UserSerializer(serializer.validated_data['user']).data,
                'token': serializer.validated_data['token'],
                'expires_at': serializer.validated_data['expires_at']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        # Récupère et désactive tous les tokens actifs de l'utilisateur
        AuthToken.objects.filter(user=request.user, is_active=True).update(is_active=False)
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)

class TokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        """Récupérer les informations sur le token actuel"""
        tokens = AuthToken.objects.filter(user=request.user, is_active=True)
        serializer = TokenSerializer(tokens, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Générer un nouveau token"""
        token = AuthToken.generate_token(request.user)
        serializer = TokenSerializer(token)
        return Response(serializer.data)
