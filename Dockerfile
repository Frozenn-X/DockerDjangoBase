# Image de base Python

FROM python:3.11

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    procps \     
    nano \       
    net-tools \ 
    wget \        
    curl \       
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement le fichier requirements.txt et installer les dépendances
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Pour la production, tu pourrais utiliser quelque chose comme :
# CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
