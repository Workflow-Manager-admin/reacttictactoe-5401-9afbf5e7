from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid

# --- Tic Tac Toe Game Logic and Data Structures ---


class GameState(str):
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"


class MoveModel(BaseModel):
    """Model for making a move."""
    row: int = Field(..., ge=0, le=2, description="Row index (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column index (0-2)")


class NewGameResponse(BaseModel):
    """Response for creating a new game."""
    game_id: str = Field(..., description="Unique game session id")
    board: List[List[str]] = Field(..., description="3x3 tic tac toe board")
    next_player: str = Field(..., description="'X' or 'O'")
    status: GameState = Field(..., description="Current game state")


class BoardResponse(BaseModel):
    """Response for retrieving the game state."""
    game_id: str = Field(..., description="Game session id")
    board: List[List[str]] = Field(..., description="3x3 tic tac toe board")
    next_player: Optional[str] = Field(
        None, description="'X', 'O', or None if game over"
    )
    status: GameState = Field(
        ..., description="Game state: in_progress, x_won, o_won, or draw"
    )
    winner: Optional[str] = Field(None, description="'X' or 'O' if someone won, or None")


class MoveResponse(BaseModel):
    """Response after a move is made."""
    board: List[List[str]] = Field(..., description="3x3 tic tac toe board")
    next_player: Optional[str] = Field(
        None, description="Next player ('X' or 'O') or None if game over"
    )
    status: GameState = Field(..., description="Game state")
    winner: Optional[str] = Field(None, description="'X', 'O', or None")
    message: str = Field(..., description="Human readable message")


# --- Singleton In-Memory Store for Game Sessions ---


class TicTacToeGame:
    """
    Handles the core logic and state for a single tic tac toe game (session).
    """

    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.next_player = "X"  # X always starts
        self.status = GameState.IN_PROGRESS
        self.winner = None

    def reset(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.next_player = "X"
        self.status = GameState.IN_PROGRESS
        self.winner = None

    def make_move(self, row: int, col: int) -> MoveResponse:
        # Only allow moves if game is in progress
        if self.status != GameState.IN_PROGRESS:
            msg = "Game is already over."
            return MoveResponse(
                board=self.board,
                next_player=None,
                status=self.status,
                winner=self.winner,
                message=msg
            )
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cell indices."
            )
        if self.board[row][col]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cell already taken."
            )

        # Make move
        self.board[row][col] = self.next_player

        # Check if this move wins or draws the game
        if self._check_winner(self.next_player):
            self.status = (
                GameState.X_WON if self.next_player == "X" else GameState.O_WON
            )
            self.winner = self.next_player
            next_player = None
            msg = f"Player {self.winner} wins!"
        elif self._is_draw():
            self.status = GameState.DRAW
            self.winner = None
            next_player = None
            msg = "It's a draw!"
        else:
            # Switch turn
            self.next_player = "O" if self.next_player == "X" else "X"
            next_player = self.next_player
            msg = "Move accepted."

        return MoveResponse(
            board=self.board,
            next_player=next_player,
            status=self.status,
            winner=self.winner,
            message=msg
        )

    def _check_winner(self, player: str) -> bool:
        b = self.board
        # Check rows, columns, diagonals
        for i in range(3):
            if all(b[i][j] == player for j in range(3)):
                return True
            if all(b[j][i] == player for j in range(3)):
                return True
        if all(b[i][i] == player for i in range(3)):
            return True
        if all(b[i][2 - i] == player for i in range(3)):
            return True
        return False

    def _is_draw(self) -> bool:
        return all(
            self.board[r][c] != "" for r in range(3) for c in range(3)
        ) and self.status == GameState.IN_PROGRESS

    def to_response(self, game_id: str) -> BoardResponse:
        return BoardResponse(
            game_id=game_id,
            board=self.board,
            next_player=self.next_player if self.status == GameState.IN_PROGRESS else None,
            status=self.status,
            winner=self.winner,
        )

    def to_new_game_response(self, game_id: str) -> NewGameResponse:
        return NewGameResponse(
            game_id=game_id,
            board=self.board,
            next_player=self.next_player,
            status=self.status
        )


# The in-memory store for all active games, mapping uuid -> TicTacToeGame instance
GAME_SESSIONS: Dict[str, TicTacToeGame] = {}

# --- FastAPI App Definition ---


app = FastAPI(
    title="Tic Tac Toe Backend API",
    description=(
        "REST API and game logic server for Tic Tac Toe application. "
        "Provides endpoints to create a game, make moves, query state, and reset games."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "TicTacToe",
            "description": "Core endpoints for playing and managing Tic Tac Toe games."
        }
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: Set proper origins in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---


# PUBLIC_INTERFACE
@app.get("/", tags=["TicTacToe"])
def health_check():
    """Health check endpoint."""
    return {"message": "Tic Tac Toe Backend is Healthy"}


# PUBLIC_INTERFACE
@app.post(
    "/games",
    response_model=NewGameResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["TicTacToe"],
    summary="Start a new Tic Tac Toe game",
    description="Creates a new game session and returns its unique ID and starting board state.",
)
def start_new_game():
    """Start a new game session."""
    game_id = str(uuid.uuid4())
    game = TicTacToeGame()
    GAME_SESSIONS[game_id] = game
    return game.to_new_game_response(game_id)


# PUBLIC_INTERFACE
@app.get(
    "/games/{game_id}",
    response_model=BoardResponse,
    tags=["TicTacToe"],
    summary="Get current game state",
    description="Get the board, current player, status, and winner for a specific game session.",
)
def get_game_state(game_id: str):
    """Retrieve the state of an existing tic tac toe game."""
    game = GAME_SESSIONS.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )
    return game.to_response(game_id)


# PUBLIC_INTERFACE
@app.post(
    "/games/{game_id}/moves",
    response_model=MoveResponse,
    tags=["TicTacToe"],
    summary="Make a move",
    description="Make a move in the specified Tic Tac Toe game (provide row and column).",
)
def make_move(game_id: str, move: MoveModel):
    """Allow the next player to make a move, and updates state or returns game over info."""
    game = GAME_SESSIONS.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )
    move_response = game.make_move(move.row, move.col)
    return move_response


# PUBLIC_INTERFACE
@app.post(
    "/games/{game_id}/restart",
    response_model=BoardResponse,
    tags=["TicTacToe"],
    summary="Restart a game",
    description="Restart the game: clears board, X starts, sets game to in_progress. Useful for rematch.",
)
def restart_game(game_id: str):
    """Restart the existing game, clearing board and resetting state."""
    game = GAME_SESSIONS.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )
    game.reset()
    return game.to_response(game_id)


# --- OpenAPI/Swagger Customization for WebSocket (not used, but future-proof notes) ---
@app.get(
    "/docs/websocket-notes",
    tags=["TicTacToe"],
    summary="Usage notes for real-time/WebSocket (not implemented)",
    description=(
        "WebSocket or real-time APIs are not part of this backend, but this endpoint notes their "
        "absence and future extension."
    ),
)
def websocket_usage_notes():
    """Simply documents that real-time multiplayer via WebSocket is not implemented."""
    note_msg = (
        "This API currently supports REST polling only. "
        "Real-time multiplayer with WebSocket could be added "
        "in future releases."
    )
    return {
        "note": note_msg
    }
