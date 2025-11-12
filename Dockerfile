# --- Étape 1 : Image de base ---
FROM python:3.12-slim

# --- Étape 2 : Répertoire de travail ---
WORKDIR /tictactoe

# --- Étape 3 : Installation de Poetry ---
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# --- Étape 4 : Dépendances ---
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main --no-interaction --no-ansi

# --- Étape 5 : Copie du code ---
COPY Back/ ./Back/
COPY Model/ ./Model/

# --- Étape 6 : Endpoint de health check minimal ---
# On crée un petit script Python pour répondre au probe de santé Azure
RUN echo "from fastapi import FastAPI\n\
app = FastAPI()\n\
@app.get('/')\ndef root():\n\
    return {'status':'ok'}" > healthcheck.py

# --- Étape 7 : Exposition du port ---
EXPOSE 8000

# --- Étape 8 : Commande d’exécution ---
# Uvicorn sur host 0.0.0.0 et port 8000
CMD ["poetry", "run", "uvicorn", "Back.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]