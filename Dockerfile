# Dockerfile

# --- Étape 1 : Image de base ---
FROM python:3.12-slim

# Définit le répertoire de travail à l'intérieur du conteneur
WORKDIR /tictactoe

# --- Étape 2 : Installation des dépendances système nécessaires ---
# (pour compiler certaines dépendances Python si besoin)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : Installation de Poetry et de ses dépendances ---
RUN pip install --no-cache-dir poetry six

# Configure Poetry pour ne pas créer de venv à l'intérieur du conteneur
RUN poetry config virtualenvs.create false

# --- Étape 4 : Installation des dépendances Python du projet ---
# Copie les fichiers de dépendances en premier pour utiliser le cache Docker
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main --no-interaction --no-ansi

# --- Étape 5 : Copie du code de l'application ---
COPY Back/ ./Back/
COPY Model/ ./Model/

# --- Étape 6 : Exposition du port ---
EXPOSE 8000

# --- Étape 7 : Commande de démarrage ---
CMD ["poetry", "run", "uvicorn", "Back.api:app", "--host", "0.0.0.0", "--port", "8000"]
