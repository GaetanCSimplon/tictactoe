from .game_logic import process_llm_turn, check_win
from .move_request import MoveRequest
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3 # Nombre de tentatives par coup

@app.post("/play")
async def play(request: MoveRequest):

    try:
        coup_joue = await process_llm_turn(
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
        # if check_win(request.grid, request.active_player_id):
        #     print("Victoire détectée pour le joueur", request.active_player_id)
        return coup_joue
    except HTTPException as e:
        raise e
    except Exception as e:
        # Lève les erreurs internes de Python
        print(f"Erreur interne non gérée: {type(e).__name__}: {e}")
        raise HTTPException(status_code=50, detail=f"Erreur inattendue : {type(e).__name__}")

@app.post("/play")
async def play(request: MoveRequest):
    llm_client = LLMClient(model_name=request.model_name)
    try:
        coup_joue = await llm_client.get_llm_move(
            grid=request.grid,
            active_player_id=request.active_player_id
        )
        # Optionnel : vérifier victoire ici

        return coup_joue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
