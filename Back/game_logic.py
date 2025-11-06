from typing import List

def format_grid_for_llm(grid: List[List[int]]) -> str:
    SYMBOL_MAP = {0: " ", 1: "X", 2: "O"}
    header = "  | " + " | ".join(str(i) for i in range(10)) + " |"
    output = header + "\n" + "-" * len(header) + "\n"
    
    for i, row in enumerate(grid):
        for cell in row:
            symbols = SYMBOL_MAP[cell]
        
    return output