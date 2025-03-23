"""
Configuration Django pour les tests.
Ce fichier importe tous les paramètres de base de settings.py,
mais remplace certaines valeurs spécifiques pour les tests.
"""

from .settings import *  # Importer tous les paramètres par défaut

# Remplacer la base de données par SQLite en mémoire pour les tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Configuration de test pour MongoDB (ne sera pas utilisée en réalité)
MONGODB_SETTINGS = {
    'db': 'test_mongo_db',
    'host': 'localhost',
    'port': 27017,
    'username': None,
    'password': None,
}

# Utiliser un algorithme de hachage plus rapide pour les mots de passe
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Désactiver le débogage pour les tests
DEBUG = False 