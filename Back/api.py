from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel, field_validator, ValidationError
from starlette.middleware.cors import CORSMiddleware

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


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/play")
def play(grid: List[List[str]]):
    # recupere la grille
    print(grid)
    # envoi au LLM
    ## prompt ingeneering
    # recup la reponse du LLM
    ### print de la réponse
    ## parser la reponse ?
    ## Verifier que c'est valide
    ## sinon je redemande au llm
    # return
    return {"row": 4, "col": 2}