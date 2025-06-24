//
// API utility functions for communicating with backend Tic Tac Toe REST API.
//

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:3001";

// PUBLIC_INTERFACE
/**
 * Start a new Tic Tac Toe game on the backend.
 * @returns {Promise<object>} The new game state.
 */
export async function startNewGame() {
  const resp = await fetch(`${API_BASE_URL}/game/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    }
  });
  if (!resp.ok) throw new Error("Could not start new game");
  return resp.json();
}

// PUBLIC_INTERFACE
/**
 * Make a move on the backend.
 * @param {string} gameId - Backend game/session ID.
 * @param {number} row - Board row (0-based).
 * @param {number} col - Board column (0-based).
 * @returns {Promise<object>} Updated game state.
 */
export async function makeMove(gameId, row, col) {
  const resp = await fetch(`${API_BASE_URL}/game/move`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ game_id: gameId, row, col })
  });
  if (!resp.ok) throw new Error("Failed to make move");
  return resp.json();
}

// PUBLIC_INTERFACE
/**
 * Get current state of a game.
 * @param {string} gameId
 * @returns {Promise<object>}
 */
export async function getGameState(gameId) {
  const resp = await fetch(`${API_BASE_URL}/game/state/${gameId}`);
  if (!resp.ok) throw new Error("Failed to get game state");
  return resp.json();
}
