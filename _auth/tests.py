from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from datetime import timedelta
import os
from .models import User, UserPermission, AuthToken
import json

# Déterminer si nous sommes dans un environnement Docker
IN_DOCKER = os.environ.get('DOCKER_CONTAINER', 'false').lower() == 'true'

class AuthTestCase(APITestCase):
    """Classe de base pour les tests d'authentification avec paramètres communs"""
    
    def setUp(self):
        """Méthode appelée avant chaque test"""
        if not IN_DOCKER:
            # Déconnecter MongoDB pour éviter les connexions inutiles en mode développement
            from mongoengine import disconnect
            disconnect()
        
        # S'assurer que la base de données est vide pour chaque test
        User.objects.all().delete()
        UserPermission.objects.all().delete()
        AuthToken.objects.all().delete()


# ----------------- Classes de test spécifiques -----------------

class RegisterEndpointTest(AuthTestCase):
    """Tests pour l'endpoint d'inscription des utilisateurs"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('auth-register')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@1234',
            'password_confirm': 'Test@1234',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_register_valid_user(self):
        """Test d'inscription avec des données valides"""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(User.objects.count(), 1)
        
    def test_register_invalid_password_confirm(self):
        """Test d'inscription avec confirmation de mot de passe non correspondante"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['password_confirm'] = 'WrongPassword'
        
        response = self.client.post(
            self.url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('password' in response.data)
        
    def test_register_duplicate_username(self):
        """Test d'inscription avec un nom d'utilisateur déjà existant"""
        # Créer un utilisateur préalablement
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='Existing@1234'
        )
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('username' in response.data)


class LoginEndpointTest(AuthTestCase):
    """Tests pour l'endpoint de connexion des utilisateurs"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('auth-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        self.valid_payload = {
            'username': 'testuser',
            'password': 'Test@1234'
        }
        
    def test_login_valid_credentials(self):
        """Test de connexion avec des identifiants valides"""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertTrue('expires_at' in response.data)
        
        # Vérifier que le token a été créé en base de données
        self.assertEqual(AuthToken.objects.filter(user=self.user, is_active=True).count(), 1)
        
    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['password'] = 'WrongPassword'
        
        response = self.client.post(
            self.url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_inactive_user(self):
        """Test de connexion avec un utilisateur inactif"""
        # Désactiver l'utilisateur
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutEndpointTest(AuthTestCase):
    """Tests pour l'endpoint de déconnexion des utilisateurs"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('auth-logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        self.token = AuthToken.generate_token(self.user)
        self.client = APIClient()
        
    def test_logout_authenticated_user(self):
        """Test de déconnexion avec un utilisateur authentifié"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.token}')
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le token a été désactivé
        self.token.refresh_from_db()
        self.assertFalse(self.token.is_active)
        
    def test_logout_unauthenticated_user(self):
        """Test de déconnexion sans authentification"""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenEndpointTest(AuthTestCase):
    """Tests pour l'endpoint de gestion des tokens"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('auth-token')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        self.token = AuthToken.generate_token(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.token}')
        
    def test_get_token_info(self):
        """Test pour récupérer les informations du token"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['token'], self.token.token)
        
    def test_generate_new_token(self):
        """Test pour générer un nouveau token"""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        
        # Vérifier que le nouveau token est différent de l'ancien
        self.assertNotEqual(response.data['token'], self.token.token)
        
        # Vérifier que l'ancien token a été désactivé
        self.token.refresh_from_db()
        self.assertFalse(self.token.is_active)
        
        # Vérifier qu'un nouveau token actif existe
        self.assertEqual(AuthToken.objects.filter(user=self.user, is_active=True).count(), 1)


class UserViewSetTest(AuthTestCase):
    """Tests pour l'endpoint de gestion des utilisateurs"""
    
    def setUp(self):
        super().setUp() 
        self.list_url = reverse('user-list')
        # Créer un utilisateur admin et un utilisateur normal
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='Admin@1234',
            is_superuser=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        
        # Création des tokens pour l'authentification
        self.admin_token = AuthToken.generate_token(self.admin)
        self.user_token = AuthToken.generate_token(self.user)
        
        # Vérifier le nombre d'utilisateurs après setup pour débogage
        user_count = User.objects.count()
        if user_count != 2:
            print(f"AVERTISSEMENT: {user_count} utilisateurs trouvés après setup, attendu: 2")
            print(f"Utilisateurs: {list(User.objects.values_list('id', 'username'))}")
        
    def test_list_users_as_admin(self):
        """Test de récupération de tous les utilisateurs en tant qu'admin"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.token}')
        response = client.get(self.list_url)
        
        # Vérifier le nombre d'utilisateurs dans la base de données
        user_count = User.objects.count()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Un admin devrait voir tous les utilisateurs (admin + testuser)
        # Les résultats sont paginés, donc on vérifie 'results' ou 'count'
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), user_count)
            usernames = [user['username'] for user in response.data['results']]
        else:
            self.assertEqual(response.data['count'], user_count)
            usernames = [user['username'] for user in response.data]
        
        self.assertIn('admin', usernames)
        self.assertIn('testuser', usernames)
        
    def test_list_users_as_regular_user(self):
        """Test de récupération des utilisateurs en tant qu'utilisateur normal"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.token}')
        response = client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Un utilisateur normal ne devrait voir que lui-même
        # Les résultats sont paginés
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['username'], 'testuser')
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['username'], 'testuser')
        
    def test_get_user_detail(self):
        """Test de récupération des détails d'un utilisateur"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.token}')
        response = client.get(f"{self.list_url}{self.user.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        
    def test_update_user_detail(self):
        """Test de mise à jour des détails d'un utilisateur"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.token}')
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = client.patch(
            f"{self.list_url}{self.user.id}/",
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')


class UserPermissionViewSetTest(AuthTestCase):
    """Tests pour l'endpoint de gestion des permissions utilisateur"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('userpermission-list')
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='Admin@1234',
            is_superuser=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@1234'
        )
        
        # Créer quelques permissions
        self.admin_permission = UserPermission.objects.create(
            user=self.admin,
            permission_name='admin_permission',
            permission_description='Permission pour admin'
        )
        self.user_permission = UserPermission.objects.create(
            user=self.user,
            permission_name='user_permission',
            permission_description='Permission pour utilisateur normal'
        )
        
        # Vérifier le nombre de permissions après setup pour débogage
        permission_count = UserPermission.objects.count()
        if permission_count != 2:
            print(f"AVERTISSEMENT: {permission_count} permissions trouvées après setup, attendu: 2")
            print(f"Permissions: {list(UserPermission.objects.values_list('id', 'permission_name'))}")
        
        self.admin_token = AuthToken.generate_token(self.admin)
        self.user_token = AuthToken.generate_token(self.user)
        
    def test_list_permissions_as_admin(self):
        """Test de récupération de toutes les permissions en tant qu'admin"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.token}')
        response = client.get(self.list_url)
        
        # Vérifier le nombre de permissions
        permission_count = UserPermission.objects.count()
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Les résultats sont paginés
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), permission_count)
        else:
            self.assertEqual(len(response.data), permission_count)
        
    def test_list_permissions_as_regular_user(self):
        """Test de récupération des permissions en tant qu'utilisateur normal"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.token}')
        response = client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Les résultats sont paginés
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)  # seulement ses permissions
            self.assertEqual(response.data['results'][0]['permission_name'], 'user_permission')
        else:
            self.assertEqual(len(response.data), 1)  # seulement ses permissions
            self.assertEqual(response.data[0]['permission_name'], 'user_permission')
        
    def test_create_permission(self):
        """Test de création d'une nouvelle permission"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.token}')
        data = {
            'user': self.user.id,
            'permission_name': 'new_permission',
            'permission_description': 'Nouvelle permission'
        }
        response = client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['permission_name'], 'new_permission')
        
        # Vérifier que la permission a été créée en base de données
        self.assertEqual(
            UserPermission.objects.filter(
                user=self.user, 
                permission_name='new_permission'
            ).count(), 
            1
        )


# Fonction utilitaire pour exécuter les tests en mode Docker
def run_integration_tests():
    """
    Utiliser cette fonction pour exécuter les tests d'intégration dans Docker
    
    Exemple depuis un script:
    ```
    # Dans un fichier run_docker_tests.py
    from _auth.tests import run_integration_tests
    if __name__ == '__main__':
        run_integration_tests()
    ```
    
    Commande: docker-compose exec web python run_docker_tests.py
    """
    import os
    import sys
    from django.test.runner import DiscoverRunner
    
    # Indiquer qu'on est dans Docker
    os.environ['DOCKER_CONTAINER'] = 'true'
    
    # Exécuter les tests
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['_auth'])
    sys.exit(bool(failures))
