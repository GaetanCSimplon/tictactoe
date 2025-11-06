from typing import List, Dict
import json
from Back.game_logic import format_grid_for_llm
from Model.model import LLMClient
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Dict
import httpx

app = FastAPI()

class MoveRequest(BaseModel):
    grid: List[List[int]]
    active_player_id: int
    model_name: str
    
    # Validation du format des données envoyées
    @field_validator('grid')
    @classmethod
    def validate_grid_dimensons(cls, v: List[List[int]]):
        GRID_SIZE = 10 # Définie la taille attendue (10x10)
        # Vérifie si le nombre de lignes envoyé correspond au GRID_SIZE
        if len(v) != GRID_SIZE:
            raise ValueError(f"La grille doit avoir {GRID_SIZE} lignes. Reçu: {len(v)}")
        # Vérifie si chaque ligne a la bonne taille (nombre de colonne = 10)
        for row in v:
            if len(row) != GRID_SIZE:
                raise ValueError(f"Toutes les lignes de la grille doivent avoir {GRID_SIZE} colonnes.")
        return v
    
    @field_validator('active_player_id')
    @classmethod
    def validate_player_id(cls, v: int):
        # Le joueur doit 1 (X) ou 2 (O)
        ALLOWED_PLAYER = {1, 2}
        
        if v not in ALLOWED_PLAYER:
            raise ValueError(f"L'ID du joueur actif doit 1 (X) ou 2 (o). Reçu: {v}")
        return v

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/play")
async def play(request: MoveRequest):
    
    # 1 - Initialisation du client LLM
    llm_client = LLMClient(model_name=request.model_name)
    
    # 2 - Utilisation de la méthode get_llm_move
    
    try:
        coup_joue = await llm_client.get_llm_move(
            grid=request.grid,
            active_player_id=request.active_player_id
        )
        return coup_joue
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne lors du traitement du coup: {e}")

