# DockerDjangoBase

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.5-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)](https://www.mongodb.com/)

</div>

Un environnement de développement Django prêt à l'emploi avec Docker, incluant MySQL et MongoDB. Une base solide pour démarrer rapidement vos projets Django avec une configuration Docker complète.

## 📋 À propos
Ce template offre un environnement de développement Django complet et prêt à l'emploi, avec une configuration Docker qui intègre à la fois MySQL et MongoDB. Il inclut également un système d'authentification personnalisé basé sur des tokens et une API REST.

### Caractéristiques principales
- **Django 5.1.5** avec Python 3.11
- **Docker** et docker-compose pour un environnement isolé
- **Double Base de Données**:
  - **MySQL 8.0** pour les données relationnelles 
  - **MongoDB** pour les données non structurées
- **API REST** avec Django REST Framework
- **Authentification par token** intégrée (sans dépendance externe)
- **Mode Développement/Production** facilement configurable

## 🚀 Démarrage rapide

### Prérequis
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation
1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/Frozenn-X/DockerDjangoBase.git
   cd DockerDjangoBase
   ```

2. Démarrez les conteneurs :
   ```bash
   docker-compose up -d
   ```

3. Accès :
   - **Application:** [http://localhost:8000](http://localhost:8000)
   - **API d'authentification:** [http://localhost:8000/auth/](http://localhost:8000/auth/)
   - **MySQL:** localhost:3306 (user: mother, password: mother2k25)
   - **MongoDB:** localhost:27017 (user: admin, password: mother2k25)

## 🔄 Modes de déploiement

### Mode Développement (par défaut)
Ce mode utilise le serveur de développement Django avec rechargement automatique.

### Mode Production
Pour passer en mode production, suivez les étapes détaillées dans la [documentation](http://localhost:8000) ou dans le fichier README.md.

## 📁 Structure du projet
```
DockerDjangoBase/
├── core/                 # Configuration principale du projet
├── _auth/                # Système d'authentification personnalisé
├── templates/            # Templates HTML
├── static/               # Fichiers statiques
├── media/                # Fichiers téléchargés
├── docker-compose.yml    # Configuration Docker Compose
├── Dockerfile            # Configuration de l'image Docker
└── requirements.txt      # Dépendances Python
```

## 🔍 Authentification API
Le projet inclut un système d'authentification par token custom:
- `/auth/register/` - Inscription d'utilisateur
- `/auth/login/` - Connexion et génération de token
- `/auth/logout/` - Déconnexion (révocation du token)
- `/auth/users/` - Gestion des utilisateurs
- `/auth/permissions/` - Gestion des permissions

## 📝 Personnalisation
Pour adapter ce template à vos besoins:

1. Modifiez les informations de connexion aux bases de données dans `docker-compose.yml`:
   ```yaml
   # Pour MySQL
   environment:
     - MYSQL_ROOT_PASSWORD=your-secure-password
     - MYSQL_DATABASE=your_db_name
     - MYSQL_USER=your_username
     - MYSQL_PASSWORD=your_password
   
   # Pour MongoDB
   environment:
     - MONGO_INITDB_ROOT_USERNAME=your_admin_user
     - MONGO_INITDB_ROOT_PASSWORD=your_secure_password
   ```

2. Ajustez les paramètres ALLOWED_HOSTS dans `core/settings.py` selon votre environnement:
   ```python
   # Développement local
   ALLOWED_HOSTS = ['localhost', '127.0.0.1']
   
   # Pour un accès sur réseau local
   ALLOWED_HOSTS = ['localhost', '127.0.0.1']
   
   # Pour production avec domaine
   ALLOWED_HOSTS = ['votredomaine.com', 'www.votredomaine.com']
   ```

3. Ajoutez vos propres applications Django

4. Personnalisez le modèle utilisateur dans `_auth/models.py` selon vos besoins

5. Configurez les permissions et les endpoints API selon votre cas d'usage

## 🤝 Contribution
Les contributions sont les bienvenues! N'hésitez pas à soumettre des pull requests ou ouvrir des issues.

## 📄 Licence
Ce projet est sous licence [MIT](LICENSE). 