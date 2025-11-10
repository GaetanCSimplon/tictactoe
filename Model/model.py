import json
import httpx
from typing import List, Dict
from fastapi import HTTPException
from Back.game_logic import format_grid_for_llm

OLLAMA_API_URL = "http://localhost:11434/api/generate"

class LLMClient:
    def __init__(self, model_name: str, max_retries: int = 5):
        self.model_name = model_name
        self.max_retries = max_retries  # essais max si coup invalide

    async def get_llm_move(self, grid: List[List[int]], active_player_id: int) -> Dict[str, int]:
        formatted_grid = format_grid_for_llm(grid)
        current_mark = "X" if active_player_id == 1 else "O"

        prompt = f"""

You are a logical and strategic AI engine playing the extended Tic-Tac-Toe game (Gomoku) on a 10x10 grid.

- "X" = Player 1  
- "O" = Player 2  
- "." = empty cell  
- Indices: row and col ∈ [0,9]

IMPORTANT:
- You must **strictly avoid** playing on any cell that already contains "X" or "O".  
- If all cells are occupied, return "pass".

Here is the current game state:
{{
  "board": {json.dumps(formatted_grid, ensure_ascii=False)},
  "to_move": "{current_mark}"
}}

Your task:
- Choose exactly one valid move and **return only JSON** in the following format:
  {{"row": <int>, "col": <int>}}
- If no legal move is possible, return:
  "pass"

Decision Rules:
1. Legal move = empty cell only  
2. Objective: align exactly 5 identical symbols  
3. Priority order: Win → Block → Double threat → Extend → Center → Edge → Smallest (row, col)  
4. Never generate explanations or text outside the JSON  
5. Absolute rule: never choose an occupied cell (doing so makes the response invalid)
"""


        system_message = """
You are a logical Gomoku game engine.

Immutable Rules:
- Respond ONLY with pure JSON: {"row": <int>, "col": <int>} or "pass"
- NEVER play on an occupied cell ("X" or "O")
- An illegal move (occupied cell) is considered a critical error
- If no legal moves exist, return only "pass"
- Never produce explanations, comments, or free text
"""


        json_payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_message,
            "stream": False,
            "options": {"temperature": 0},
            "format": "json"
        }

        # Retry si le LLM propose une case occupée
        for _ in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    response = await client.post(OLLAMA_API_URL, json=json_payload)
                    response.raise_for_status()
                    data = response.json()
                    json_string = data.get("response")
                    if not json_string:
                        continue

                    coup_joue = json.loads(json_string)

                    # Coup valide {"row": int, "col": int}
                    if isinstance(coup_joue, dict) and "row" in coup_joue and "col" in coup_joue:
                        r, c = coup_joue["row"], coup_joue["col"]
                        if 0 <= r <= 9 and 0 <= c <= 9 and grid[r][c] == 0:
                            return {"row": r, "col": c}
                        else:
                            continue  # case occupée → retry

                    # Cas "pass"
                    if isinstance(coup_joue, str) and coup_joue.strip().lower() == "pass":
                        return {"pass": True}

            except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError):
                continue

        # Si toutes les tentatives échouent
        return {"pass": True}
