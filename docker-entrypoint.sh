#!/bin/bash
   
   # Attendre que MySQL soit prêt
   python -c 'import time, MySQLdb; \
     while True: \
       try: \
         MySQLdb.connect(host="db_mysql_core", user="mother", passwd="mother2k25", db="db_mysql_core"); \
         break; \
       except MySQLdb.OperationalError: \
         print("MySQL not ready yet... waiting"); \
         time.sleep(2);'
   
   # Appliquer les migrations
   python manage.py migrate
   
   # Démarrer le serveur
   python manage.py runserver 0.0.0.0:8000