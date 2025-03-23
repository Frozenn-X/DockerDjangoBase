#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Date et heure de l'exécution
echo "===== DJANGO TEST LOGS - $(date) =====" > test_logs.txt
echo "Environnement: $(uname -a)" >> test_logs.txt
echo "Python: $(python --version 2>&1)" >> test_logs.txt
echo "Django: $(python -c 'import django; print(django.get_version())' 2>&1)" >> test_logs.txt
echo "=====================================" >> test_logs.txt
echo >> test_logs.txt

# Fonction pour logger à la fois sur la console et dans le fichier
log() {
    local message="$1"
    local color="$2"
    echo -e "${color}${message}${NC}" | tee -a test_logs.txt
}

log "Exécution des tests unitaires avec verbosité maximale..." "$BLUE"
log "Les résultats seront sauvegardés dans test_logs.txt" "$BLUE"
log "" ""

# Exécuter les tests avec la verbosité maximale et enregistrer la sortie
DJANGO_SETTINGS_MODULE=core.test_settings python manage.py test _auth -v 3 2>&1 | tee -a test_logs.txt

# Vérifier si les tests ont réussi
if [ ${PIPESTATUS[0]} -eq 0 ]; then
  log "Les tests ont réussi !" "$GREEN"
  log "Résultats enregistrés dans test_logs.txt" "$GREEN"
  exit 0
else
  log "Des erreurs ont été détectées dans les tests !" "$RED"
  log "Consultez test_logs.txt pour plus de détails." "$RED"
  exit 1
fi 