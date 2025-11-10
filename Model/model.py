import json
import httpx
from typing import List, Dict
from fastapi import HTTPException
from Back.game_logic import format_grid_for_llm

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def format_grid_for_llm(grid: List[List[int]]) -> str:
    """
    Convertit la grille numérique (0, 1, 2) en un format texte
    lisible par le LLM (avec indices de lignes/colonnes).
    """
    SYMBOL_MAP = {0: " ", 1: "X", 2: "O"} # Utilise " " pour vide
    header = "   | " + " | ".join(str(i) for i in range(10)) + " |"
    output = header + "\n" + "-" * len(header) + "\n"
    
    for i, row in enumerate(grid):
        # Conversion de chaque entier de 'row' en son symbole
        symbols = [SYMBOL_MAP[cell] for cell in row]
        # Jointure des symboles
        line_content = " | ".join(symbols)
        # Ajout de l'indice de ligne formaté
        output += f"{i:2} | {line_content} |\n"
        
    return output

class LLMClient:
    def __init__(self, model_name: str, max_retries: int = 5):
        self.model_name = model_name
        self.max_retries = max_retries  # essais max si coup invalide

    async def get_llm_move(self, grid: List[List[int]], active_player_id: int) -> Dict[str, int]:
        formatted_grid = format_grid_for_llm(grid)
        current_mark = "X" if active_player_id == 1 else "O"

        prompt = f"""
        You are playing a Tic-Tac-Toe game on a 10x10 board. Two players alternate placing their marks: Player 1 uses 'x' and Player 2 uses 'o'. The goal is to align exactly 5 marks consecutively horizontally, vertically, or diagonally.

        Current game state (' ' for empty cells):
        {formatted_grid}

        Players alternate turns to avoid filling entire rows, columns, or diagonals completely.
        The last move was played by Player {last_player_id}, but you should focus on the entire board state.
        It is now Player {active_player_id}'s turn, who plays as '{current_mark}'. Your model's name is '{self.model_name}'.
        Given this board state and rules, select the best move for Player {active_player_id} and respond ONLY with a JSON object containing the keys 'row' and 'col' for your chosen move (1-based indices).

        If no valid moves remain, respond with 'pass'.
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
