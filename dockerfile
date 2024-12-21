# Utiliser une image Python comme base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app
ENV FLASK_APP=app.py

ENV FLASK_RUN_HOST=0.0.0.0
# Copier les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par Flask
EXPOSE 5000

# Lancer l'application
CMD ["flask", "run", "--host=0.0.0.0", "--port", "5000"]

