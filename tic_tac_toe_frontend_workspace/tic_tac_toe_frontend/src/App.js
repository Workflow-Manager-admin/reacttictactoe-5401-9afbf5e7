import React, { useEffect, useState, useCallback } from "react";
import "./App.css";
import "./components/Board.css";
import Board from "./components/Board";
import GameControls from "./components/GameControls";
import Scoreboard from "./components/Scoreboard";
import { startNewGame, makeMove, getGameState } from "./api";

// Utility: empty 3x3 board
function emptyBoard() {
  return [
    [null, null, null],
    [null, null, null],
    [null, null, null],
  ];
}

function getInitialScores() {
  return { X: 0, O: 0, draws: 0 };
}

function App() {
  // Game state
  const [gameId, setGameId] = useState(null);
  const [board, setBoard] = useState(emptyBoard());
  const [currentPlayer, setCurrentPlayer] = useState("X");
  const [winner, setWinner] = useState(null);
  const [draw, setDraw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scores, setScores] = useState(getInitialScores());
  const [errorMsg, setErrorMsg] = useState("");

  // Start new game, resetting all state and session
  const handleNewGame = useCallback(async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const data = await startNewGame();
      setGameId(data.game_id);
      setBoard(data.board);
      setCurrentPlayer(data.current_player);
      setWinner(null);
      setDraw(false);
    } catch (error) {
      setErrorMsg("Could not start new game. Check backend connection.");
    }
    setLoading(false);
  }, []);

  // Restart game in existing session (game_id)
  const handleRestart = useCallback(async () => {
    if (!gameId) {
      handleNewGame();
      return;
    }
    setLoading(true);
    setErrorMsg("");
    try {
      const data = await startNewGame();
      setGameId(data.game_id);
      setBoard(data.board);
      setCurrentPlayer(data.current_player);
      setWinner(null);
      setDraw(false);
    } catch (error) {
      setErrorMsg("Could not restart game.");
    }
    setLoading(false);
  // eslint-disable-next-line
  }, [gameId]);

  // Handle cell click (row,col)
  const handleCellClick = async (row, col) => {
    // Block moves if winner or draw
    if (winner || draw || loading) return;

    setLoading(true);
    setErrorMsg("");

    try {
      const data = await makeMove(gameId, row, col);
      setBoard(data.board);
      setCurrentPlayer(data.current_player);
      setWinner(data.winner);
      setDraw(data.draw);
      if (data.winner) {
        setScores((prev) => ({ ...prev, [data.winner]: prev[data.winner] + 1 }));
      } else if (data.draw) {
        setScores((prev) => ({ ...prev, draws: prev.draws + 1 }));
      }
    } catch (error) {
      setErrorMsg("Failed to make move. Try again.");
    }
    setLoading(false);
  };

  // On first load, start new game
  useEffect(() => { handleNewGame(); }, []);

  return (
    <div className="app">
      <nav className="navbar">
        <div className="container">
          <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
            <div className="logo">
              <span className="logo-symbol">*</span> KAVIA AI
            </div>
            <button className="btn" onClick={handleNewGame} disabled={loading}>
              New Game
            </button>
          </div>
        </div>
      </nav>

      <main>
        <div className="tic-tac-toe-container">
          <h1 className="title" style={{ marginBottom: "8px", marginTop: 0 }}>
            Tic Tac Toe
          </h1>
          <div className="description">
            Play classic Tic Tac Toe! Take turns with another player (X and O) and try to win.<br hidden />The board below syncs with the backend game engine.
          </div>

          <Scoreboard scores={scores} />

          <Board
            board={board}
            onCellClick={handleCellClick}
            disabled={loading || Boolean(winner) || draw}
          />

          <GameControls
            currentPlayer={currentPlayer}
            winner={winner}
            draw={draw}
            onNewGame={handleNewGame}
            onRestart={handleRestart}
            loading={loading}
          />
          {errorMsg && (
            <div style={{ color: "#d32f2f", fontSize: "1rem", marginTop: "6px" }}>
              {errorMsg}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;