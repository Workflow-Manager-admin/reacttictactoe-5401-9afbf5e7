import React from "react";

// PUBLIC_INTERFACE
/**
 * GameControls displays current player, game controls, and status.
 * 
 * Props:
 *  - currentPlayer: 'X' | 'O'
 *  - winner: 'X' | 'O' | null
 *  - draw: boolean
 *  - onNewGame(): void
 *  - onRestart(): void
 *  - loading: boolean
 */
function GameControls({
  currentPlayer,
  winner,
  draw,
  onNewGame,
  onRestart,
  loading
}) {
  let status = "";
  if (winner) status = `🏆 Winner: ${winner}`;
  else if (draw) status = "🤝 Draw";
  else status = `Next: ${currentPlayer || '-'}`;

  return (
    <div className="controls-section">
      <div className="status-label">{status}</div>
      <div className="game-buttons">
        <button className="btn" onClick={onNewGame} disabled={loading}>
          New Game
        </button>
        <button className="btn" onClick={onRestart} disabled={loading}>
          Restart
        </button>
      </div>
    </div>
  );
}

export default GameControls;
