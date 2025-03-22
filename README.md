# DockerDjangoBase

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.5-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)](https://www.mongodb.com/)

</div>

Un environnement de développement Django prêt à l'emploi avec Docker, incluant MySQL et MongoDB. Une base solide pour démarrer rapidement vos projets Django avec une configuration Docker complète.

## 🚀 Fonctionnalités

- **Django 5.1.5** avec Python 3.11
- **MySQL 8.0** pour les données relationnelles
- **MongoDB** pour les données non structurées
- **API REST** complète avec Django REST Framework
- **Authentification personnalisée** avec système de tokens
- **Docker et docker-compose** pour un environnement isolé et reproductible
- **Configuration de développement optimisée**
- **Multi-base de données** prête à l'emploi

## 📚 Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🔧 Installation

### Clonez le dépôt et démarrez les conteneurs:

```bash
git clone https://github.com/yourusername/DockerDjangoBase.git
cd DockerDjangoBase
docker-compose up -d
```

### Premier démarrage

Lors du premier démarrage, la structure de base du projet est automatiquement mise en place:

1. Les bases de données MySQL et MongoDB sont initialisées
2. Les migrations Django sont appliquées
3. Les fichiers statiques sont collectés

## 📋 Structure du projet

```
DockerDjangoBase/
├── core/                 # Configuration principale du projet Django
├── _auth/                # Application d'authentification personnalisée
├── templates/            # Templates HTML
├── static/               # Fichiers statiques (CSS, JS, images)
├── media/                # Fichiers téléchargés par les utilisateurs
├── docker-compose.yml    # Configuration Docker Compose
├── Dockerfile            # Image Docker pour le service web
├── requirements.txt      # Dépendances Python
└── manage.py             # Script de gestion Django
```

## 🌐 Accès

- **Application Django**: [http://localhost:8000](http://localhost:8000)
- **Interface Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **API d'authentification**: [http://localhost:8000/auth/](http://localhost:8000/auth/)
- **MySQL**:
  - **Hôte**: localhost
  - **Port**: 3306
  - **Utilisateur**: mother
  - **Mot de passe**: mother2k25
  - **Base de données**: db_mysql_core
- **MongoDB**:
  - **Hôte**: localhost
  - **Port**: 27017
  - **Utilisateur**: admin
  - **Mot de passe**: mother2k25

## 🛠 Commandes utiles

```bash
# Démarrer tous les services
docker-compose up

# Démarrer tous les services en arrière-plan
docker-compose up -d

# Accéder au shell du conteneur web
docker-compose exec web bash

# Créer un superutilisateur Django
docker-compose exec web python manage.py createsuperuser

# Effectuer des migrations Django
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic

# Arrêter tous les services
docker-compose down

# Arrêter tous les services et supprimer les volumes
docker-compose down -v
```

## 🔍 Développement

### Authentification API

Le système d'authentification personnalisé fournit:

- Inscription et connexion d'utilisateurs
- Authentification par tokens
- Gestion des permissions utilisateurs
- API REST complète pour toutes les opérations d'authentification

### Bases de données

- **MySQL**: Utilisé pour les données relationnelles et la plupart des modèles Django
- **MongoDB**: Disponible pour les données non structurées ou les modèles nécessitant plus de flexibilité

## 🚀 Modes de déploiement

### Mode développement (actuel)

Par défaut, le projet démarre en mode développement avec le serveur Django intégré :

```bash
# Dans le Dockerfile (configuration actuelle)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Ce mode est idéal pour le développement car il offre :
- Rechargement automatique du code
- Messages d'erreur détaillés
- Débogage facilité

### Mode production (WSGI)

Pour le déploiement en production, le projet peut utiliser Gunicorn comme serveur WSGI :

```bash
# Configuration pour production
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

Avantages du mode production :
- Performances optimisées
- Meilleure gestion des requêtes concurrentes
- Configuration sécurisée (DEBUG=False)
- Serveur multi-processus

## 🔄 Passage en mode Production

Pour passer du mode Développement au mode Production, suivez ces étapes :

1. **Modifiez le Dockerfile**

   Ouvrez le fichier `Dockerfile` et modifiez la dernière ligne :
   ```diff
   - CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
   + CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
   ```

   Ajoutez également l'installation de Gunicorn :
   ```diff
   RUN pip install --no-cache-dir -r requirements.txt
   + RUN pip install --no-cache-dir gunicorn
   ```

2. **Configurez Django pour la production**

   Dans `core/settings.py` :
   ```python
   # Passez en mode production
   DEBUG = False
   
   # Configurez les hôtes autorisés (remplacez par vos domaines)
   ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']
   ```

3. **Collectez les fichiers statiques**

   ```bash
   # Assurez-vous que vos dossiers statiques sont configurés dans settings.py
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **Reconstruisez et redémarrez les conteneurs**

   ```bash
   # Reconstruire l'image après modification du Dockerfile
   docker-compose build web
   
   # Redémarrer les services
   docker-compose up -d
   ```

5. **Vérification**

   Accédez à votre application pour vérifier qu'elle fonctionne correctement en mode production :
   ```
   http://localhost:8000
   ```

⚠️ **Note importante** : En production, assurez-vous de :
- Utiliser des mots de passe sécurisés
- Configurer correctement HTTPS
- Régler les paramètres ALLOWED_HOSTS avec vos domaines spécifiques
- Désactiver les messages d'erreur détaillés (DEBUG = False)

## 📝 Licence

Ce projet est sous licence [MIT](LICENSE).

 
