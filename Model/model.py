
# from dotenv import load_dotenv # Récuperer variables d'environnement
import os
import requests
# from move_request import Movequest


# Charger les variables du fichier .env
# load_dotenv()

# Accéder aux variables
api_key = os.getenv("API_KEY") # récupérer la clé APi à partir d'Azure foundry
debug = os.getenv("DEBUG") == "True" # os.getenv("DEBUG") lit la variable d’environnement DEBUG (ex. "True").Elle compare le résultat à la chaîne "True".Si c'est égal, la variable debug devient le booléen True.

import requests

ollama_url = "http://localhost:11434"
model_name = "gemma3:1b"

# Exemple minimaliste de grille formatée (à ajuster dynamiquement)
format_grid_for_llm = "\n".join([".".join(["." for _ in range(10)]) for _ in range(10)])

# Variables dynamiques de test — à remplacer en fonction de ta logique métier
last_player_id = 1
last_move_coords = "5,5"
active_player_id = 2
current_mark = "o"

prompt = f"""You are playing a Tic-Tac-Toe game on a 10x10 board. Two players alternate placing their marks: Player 1 uses 'x' and Player 2 uses 'o'. The goal is to align 5 marks in a row horizontally, vertically, or diagonally.
Current game state ('.' for empty cells):
{format_grid_for_llm}
The last move was played by Player {last_player_id}, and the coordinates were {last_move_coords}.
You are Player {active_player_id} playing as '{current_mark}'. Your model's name is '{model_name}'.
Given this state, choose the best move to play next. Respond ONLY with the coordinates as two numbers separated by a comma (row,column), starting at 1,1 for the top-left cell.
If no moves are possible, respond with 'pass'.
"""

response = requests.post(f"{ollama_url}/api/generate", json={
    "model": model_name,
    "prompt": prompt,
    "stream": False,
    "system": """You are a Tic-Tac-Toe player. In Tic-Tac-Toe,
    two players take turns placing their marks (an 'x' for player 'x' and an 'o' for player 'o')
    on a 10x10 grid. The goal is to get 5 of your marks in a row, either horizontally, vertically,
    or diagonally. If all spaces on the grid are filled and neither player has achieved five in a row,
    the game ends in a draw.""",
    "options": {
        "temperature": 1
    },
    "format": {
        "type": "array",
        "items": {"type": "number"},
        "minContains": 2,
        "maxContains": 2
    }
})

print("Status code:", response.status_code)
# print("Response JSON:", response.json())
print("Response JSON:", response.json()["response"][0])