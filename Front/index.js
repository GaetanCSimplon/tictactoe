const urlAPI = "http://127.0.0.1:8000/play"

// Variables liées à la grille de jeu
const GRID_SIZE = 10;
const grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0));
// Variable liée au joueur
let activePlayerId = 1; // 1 pour 'X'
// Sélection du conteneur DOM
const gridHTML = document.querySelector("#grid")
// Variable de sélection du modèle
const llmModelName = "gemma3:1b"

// Fonction d'affichage de la grille
function viewGrid() {
    gridHTML.innerHTML = ""
    for (let row of grid) {
        for (let cell of row) {
            const cellHTML = document.createElement("div")
            cellHTML.classList.add("cell")
            cellHTML.textContent = cell === 1 ? "X" : cell === 2 ? "O" : ""
            gridHTML.appendChild(cellHTML)
        }
    }
}

// Interaction bouton Play
document.querySelector("#play").addEventListener("click", e => {
    const requestData = {
        grid: grid,
        active_player_id: activePlayerId,
        model_name: llmModelName
    };

    fetch(urlAPI, {
        method: "POST",
        body: JSON.stringify(requestData),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)

        // Si LLM passe le tour
        if (data.pass) {
            console.log("Aucun coup possible, tour passé")
            activePlayerId = activePlayerId === 1 ? 2 : 1
            return
        }

        // Vérifier que les coordonnées existent et la case est vide
        if (typeof data.row === "number" && typeof data.col === "number") {
            if (grid[data.row][data.col] === 0) {
                grid[data.row][data.col] = activePlayerId
                viewGrid()
                activePlayerId = activePlayerId === 1 ? 2 : 1
            } else {
                console.error("Le LLM a proposé une case déjà occupée", data)
            }
        } else {
            console.error("Réponse LLM invalide", data)
        }
    })
    .catch(err => console.error("Erreur API:", err))
})
