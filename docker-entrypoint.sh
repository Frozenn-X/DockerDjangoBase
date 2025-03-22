#!/bin/bash
set -e

# Configuration des couleurs pour le logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} ${timestamp} - ${message}"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} ${timestamp} - ${message}"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} - ${message}"
            ;;
        "DEBUG")
            if [[ "${DEBUG}" == "true" ]]; then
                echo -e "${BLUE}[DEBUG]${NC} ${timestamp} - ${message}"
            fi
            ;;
        *)
            echo -e "${timestamp} - ${message}"
            ;;
    esac
}

# Gestionnaire de signal pour arrêt propre
handle_sigterm() {
    log "INFO" "Reçu signal de terminaison. Arrêt propre en cours..."
    
    # Tuer les processus en arrière-plan si nécessaires
    if [[ -n "${SERVER_PID}" ]]; then
        kill -TERM "${SERVER_PID}" 2>/dev/null || true
    fi
    
    exit 0
}

# Configuration du gestionnaire de signal
trap 'handle_sigterm' SIGTERM SIGINT

# Fonction d'attente pour les bases de données
wait_for_db() {
    local db_type=$1
    local host=$2
    local port=$3
    local user=$4
    local password=$5
    local database=$6
    local max_attempts=$7
    local attempt=1
    
    log "INFO" "En attente de la disponibilité de ${db_type} sur ${host}:${port}..."
    
    while [ $attempt -le $max_attempts ]; do
        if [ "$db_type" = "mysql" ]; then
            if python -c "import MySQLdb; MySQLdb.connect(host='$host', user='$user', passwd='$password', db='$database', connect_timeout=5)" &>/dev/null; then
                log "INFO" "${db_type} est disponible après $attempt tentatives"
                return 0
            fi
        elif [ "$db_type" = "mongodb" ]; then
            if python -c "import pymongo; pymongo.MongoClient('mongodb://$user:$password@$host:$port/$database', serverSelectionTimeoutMS=5000).server_info()" &>/dev/null; then
                log "INFO" "${db_type} est disponible après $attempt tentatives"
                return 0
            fi
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR" "Impossible de se connecter à ${db_type} après $max_attempts tentatives"
            return 1
        fi
        
        attempt=$((attempt+1))
        log "WARN" "Tentative $attempt/$max_attempts: ${db_type} n'est pas encore prêt..."
        sleep 2
    done
}

# Fonction pour créer un superutilisateur si nécessaire
create_superuser() {
    if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD}" ]]; then
        log "INFO" "Vérification de l'existence du superutilisateur ${DJANGO_SUPERUSER_USERNAME}..."
        
        # Vérifier si le superutilisateur existe déjà
        if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists())" | grep -q "True"; then
            log "INFO" "Le superutilisateur ${DJANGO_SUPERUSER_USERNAME} existe déjà"
        else
            log "INFO" "Création du superutilisateur ${DJANGO_SUPERUSER_USERNAME}..."
            python manage.py createsuperuser --noinput
            if [ $? -eq 0 ]; then
                log "INFO" "Superutilisateur créé avec succès"
            else
                log "ERROR" "Échec lors de la création du superutilisateur"
            fi
        fi
    else
        log "DEBUG" "Variables d'environnement pour le superutilisateur non définies, aucun superutilisateur créé"
    fi
}

# Fonction pour appliquer les migrations Django
apply_migrations() {
    log "INFO" "Application des migrations Django..."
    
    python manage.py migrate
    
    if [ $? -eq 0 ]; then
        log "INFO" "Migrations appliquées avec succès"
    else
        log "ERROR" "Échec lors de l'application des migrations"
        return 1
    fi
    
    return 0
}

# Fonction pour collecter les fichiers statiques
collect_static() {
    if [[ "${DJANGO_ENV}" == "production" ]]; then
        log "INFO" "Collecte des fichiers statiques..."
        python manage.py collectstatic --noinput
        
        if [ $? -eq 0 ]; then
            log "INFO" "Fichiers statiques collectés avec succès"
        else
            log "WARN" "Échec lors de la collecte des fichiers statiques"
        fi
    else
        log "DEBUG" "Environnement de développement: pas de collecte des fichiers statiques"
    fi
}

# Fonction principale
main() {
    # Déterminer l'environnement (dev ou prod)
    DJANGO_ENV=${DJANGO_ENV:-development}
    DEBUG=${DEBUG:-false}
    
    log "INFO" "Démarrage en mode ${DJANGO_ENV}"
    
    # Attendre que les bases de données soient prêtes
    wait_for_db "mysql" "db_mysql_core" "3306" "mother" "mother2k25" "db_mysql_core" 30 || exit 1
    wait_for_db "mongodb" "db_mongo_core" "27017" "admin" "mother2k25" "admin" 30 || log "WARN" "MongoDB n'est pas disponible, mais le démarrage continue"
    
    # Appliquer les migrations Django
    apply_migrations || exit 1
    
    # Collecter les fichiers statiques (en production)
    collect_static
    
    # Créer un superutilisateur si nécessaire
    create_superuser
    
    # Démarrer l'application selon l'environnement
    if [[ "${DJANGO_ENV}" == "production" ]]; then
        log "INFO" "Démarrage de Gunicorn (mode production)..."
        exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
    else
        log "INFO" "Démarrage du serveur de développement Django..."
        python manage.py runserver 0.0.0.0:8000 &
        SERVER_PID=$!
        wait $SERVER_PID
    fi
}

# Exécuter la fonction principale
main