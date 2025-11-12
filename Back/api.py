from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from .move_request import MoveRequest
from .game_logic import process_llm_turn, check_win, is_grid_full

app = FastAPI(title="Tic Tac Toe Backend")

# --- CORS CONFIGURATION ---
origins = [
    "https://zealous-stone-0b1da0103.3.azurestaticapps.net",  # ton front déployé sur Azure
    "http://localhost:5500",  # utile pour les tests locaux
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3

@app.get("/")
async def root():
    return {"message": "API Tic-Tac-Toe opérationnelle 🎯"}

@app.post("/play")
async def play(request: MoveRequest):
    try:
        coup_joue = await process_llm_turn(
            grid=request.grid,
            active_player_id=request.active_player_id,
            model_name=request.model_name,
            max_retries=MAX_RETRIES
        )

        row, col = coup_joue["row"], coup_joue["col"]
        temp_grid = [r[:] for r in request.grid]
        temp_grid[row][col] = request.active_player_id

        is_winner = check_win(temp_grid, request.active_player_id, row, col)
        is_draw = not is_winner and is_grid_full(temp_grid)

        return {
            "row": row,
            "col": col,
            "player_id": request.active_player_id,
            "is_winner": is_winner,
            "is_draw": is_draw
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Échec du LLM : {e}")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Serveur LLM (Azure) injoignable.")
    except Exception as e:
        print(f"Erreur interne non gérée: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne inattendue : {type(e).__name__}")
