from typing import List

def format_grid_for_llm(grid: List[List[int]]) -> str:
    SYMBOL_MAP = {0: " ", 1: "X", 2: "O"}
    header = "  | " + " | ".join(str(i) for i in range(10)) + " |"
    output = header + "\n" + "-" * len(header) + "\n"
    
    for i, row in enumerate(grid):
        # Conversion de chaque entier de 'row' en son symbole (dans SYMBOL_MAP)
        symbols = [SYMBOL_MAP[cell] for cell in row]
        # Jonture des symboles par '|', ajout de l'indice de ligne et formatage
        line_content = " | " .join(symbols)
        # Centrage du symbole dans la grille
        output += f"{i:2} | {line_content} |\n"
    return output


# from typing import List

# def format_grid_for_llm(grid: List[List[int]]) -> List[str]:
#     """
#     Convertit la grille interne (0,1,2) en liste de chaînes de 10 caractères.
#     0 -> '.', 1 -> 'X', 2 -> 'O'
#     Utilisé pour le prompt LLM.
#     """
#     SYMBOL_MAP = {0: ".", 1: "X", 2: "O"}
#     return ["".join(SYMBOL_MAP[cell] for cell in row) for row in grid]


def check_win(grid: List[List[int]], player_id: int) -> bool:
    """
    Vérifie si le joueur 'player_id' a exactement 5 symboles alignés.
    Retourne True si victoire, sinon False.
    """
    SIZE = 10
    target = player_id
    directions = [
        (0, 1),  # horizontal
        (1, 0),  # vertical
        (1, 1),  # diagonale descendante
        (1, -1)  # diagonale montante
    ]

    for row in range(SIZE):
        for col in range(SIZE):
            if grid[row][col] != target:
                continue
            for dr, dc in directions:
                count = 1
                r, c = row + dr, col + dc
                while 0 <= r < SIZE and 0 <= c < SIZE and grid[r][c] == target:
                    count += 1
                    r += dr
                    c += dc

                # Vérifie exactement 5 symboles
                if count == 5:
                    # Vérifie qu’il n’y a pas de symbole supplémentaire avant/après la séquence
                    prev_r, prev_c = row - dr, col - dc
                    next_r, next_c = row + dr*5, col + dc*5
                    before_ok = not (0 <= prev_r < SIZE and 0 <= prev_c < SIZE and grid[prev_r][prev_c] == target)
                    after_ok = not (0 <= next_r < SIZE and 0 <= next_c < SIZE and grid[next_r][next_c] == target)
                    if before_ok and after_ok:
                        return True
    return False
