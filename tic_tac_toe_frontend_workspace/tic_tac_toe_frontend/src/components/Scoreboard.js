import React from "react";

/**
 * Scoreboard shows counts of X wins, O wins, and draws.
 * 
 * Props:
 *  - scores: { X: number, O: number, draws: number }
 */
function Scoreboard({ scores }) {
  return (
    <div className="scoreboard-container">
      <div className="score score-x">X: {scores.X}</div>
      <div className="score score-o">O: {scores.O}</div>
      <div className="score score-draw">Draws: {scores.draws}</div>
    </div>
  );
}
export default Scoreboard;
