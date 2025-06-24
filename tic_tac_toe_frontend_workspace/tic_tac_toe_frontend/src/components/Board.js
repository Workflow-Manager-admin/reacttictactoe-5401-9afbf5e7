import React from "react";
import "./Board.css";

/**
 * Board component: displays the 3x3 tic-tac-toe grid.
 * 
 * Props:
 *  - board: 2D array (3x3) of 'X', 'O', or null
 *  - onCellClick: function(row: number, col: number)
 *  - disabled: bool -- disables cell clicks (not user's turn/etc)
 */
function Board({ board, onCellClick, disabled }) {
  return (
    <div className="ttt-board">
      {board.map((row, rIdx) => (
        <div className="ttt-row" key={rIdx}>
          {row.map((cell, cIdx) => (
            <button
              key={cIdx}
              className="ttt-cell"
              disabled={disabled || cell !== null}
              onClick={() => onCellClick(rIdx, cIdx)}
              aria-label={`Cell ${rIdx + 1}, ${cIdx + 1}${cell ? ", occupied" : ""}`}
            >
              {cell}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}

export default Board;
