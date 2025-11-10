from typing import List, Dict
from .game_logic import format_grid_for_llm
from Model.model import LLMClient
from .move_request import MoveRequest
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import httpx

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3 # Nombre de tentatives

@app.post("/play")
async def play(request: MoveRequest):
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
    # 1 - Initialisation du client LLM
    llm_client = LLMClient(OLLAMA_API_URL=request.model_name)
    
    # 2 - Utilisation de la méthode get_llm_move
    
    try:
        coup_joue = await llm_client.get_llm_move(
            grid=request.grid,
            active_player_id=request.active_player_id,
            model_name=request.model_name,
            max_retries=MAX_RETRIES
        )
        # Créer une grille temporaire pour appliquer le coup
        temp_grid = [row[:] for row in request.grid]
        row = coup_joue["row"]
        col = coup_joue["col"]
        
        # Appliquer le coup du LLM sur la grille temporaire
        temp_grid[row][col] = request.active_player_id
        
        # Appelle la 
        is_winner = check_win(
            temp_grid,
            request.active_player_id,
            row,
            col
        )
        
        return {
            "row": row,
            "col": col,
            "is_winner": is_winner,
            "player_id": request.active_player_id
        }
    except ValueError as e:
        # Erreur levée par process_llm_turn si les 3 tentatives échouent
        raise HTTPException(status_code=400, detail=f"Echec du LLM : {e}")
    except httpx.ConnectError:
        # Erreur si Ollama n'est pas joignable
        raise HTTPException(status_code=503, detail="Ollama injoignable.")
    except Exception as e:
        # Lève les erreur 500/502 par le LLMCLient
        raise e
    except Exception as e:
        # Lève les erreurs internes de Python
        print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
        raise HTTPException(status_code=50, detail=f"Erreur inattendue : {type(e).__name__}")