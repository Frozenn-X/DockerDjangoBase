from django.db import models
from django.contrib.auth.models import AbstractUser
from mongoengine import Document, StringField, DateTimeField, DictField, ReferenceField, ListField
from datetime import datetime, timedelta
import pytz
import secrets
from django.utils import timezone


class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.username


class UserPermission(models.Model):
    """Modèle de permission personnalisée"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    permission_name = models.CharField(max_length=100)
    permission_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'permission_name')
        verbose_name = 'Permission utilisateur'
        verbose_name_plural = 'Permissions utilisateur'
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_name}"


# Modèle MongoDB pour les logs d'activité
class UserActivityLog(Document):
    """Modèle pour stocker les logs d'activité utilisateur dans MongoDB"""
    user_id = StringField(required=True)  # ID de l'utilisateur Django
    action = StringField(required=True)  # Type d'action (login, logout, update_profile, etc.)
    timestamp = DateTimeField(default=datetime.now(pytz.UTC))
    details = DictField()  # Détails flexibles de l'action
    ip_address = StringField()
    user_agent = StringField()
    status = StringField(choices=['success', 'failure', 'pending'])
    metadata = DictField()  # Données supplémentaires flexibles

    meta = {
        'collection': 'user_activity_logs',
        'indexes': [
            'user_id',
            'action',
            'timestamp',
            'status'
        ]
    }

    def __str__(self):
        return f"{self.user_id} - {self.action} - {self.timestamp}"

    @classmethod
    def log_activity(cls, user_id, action, details=None, ip_address=None, user_agent=None, status='success', metadata=None):
        """Méthode utilitaire pour créer un nouveau log"""
        return cls(
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            metadata=metadata or {}
        ).save()

# # Créer un log d'activité
# UserActivityLog.log_activity(
#     user_id="123",
#     action="login",
#     details={"browser": "Chrome", "device": "desktop"},
#     ip_address="192.168.1.1",
#     user_agent="Mozilla/5.0...",
#     metadata={"session_duration": 3600}
# )

# # Rechercher des logs
# logs = UserActivityLog.objects(
#     user_id="123",
#     action="login",
#     timestamp__gte=datetime.utcnow() - timedelta(days=7)
# )

class AuthToken(models.Model):
    """Token d'authentification pour les utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Token for {self.user.username} ({self.token[:10]}...)"
    
    def is_valid(self):
        """Vérifie si le token est valide (actif et non expiré)"""
        return self.is_active and self.expires_at > timezone.now()
    
    @classmethod
    def generate_token(cls, user, expiry_days=7):
        """Génère un nouveau token pour l'utilisateur"""
        # Désactive les tokens précédents de l'utilisateur
        cls.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Crée un nouveau token
        token = secrets.token_hex(32)  # 64 caractères
        expires_at = timezone.now() + timedelta(days=expiry_days)
        
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    @classmethod
    def get_user_from_token(cls, token):
        """Récupère l'utilisateur associé à un token valide"""
        try:
            token_obj = cls.objects.get(token=token, is_active=True)
            if token_obj.expires_at > timezone.now():
                return token_obj.user
            else:
                # Désactive le token expiré
                token_obj.is_active = False
                token_obj.save()
                return None
        except cls.DoesNotExist:
            return None