from enum import Enum, auto

# Board dimensions
BOARD_SIZE = 8
BOARD_ROWS = 8
BOARD_COLS = 8

# Starting row indices
WHITE_BACK_ROW = 7
WHITE_PAWN_ROW = 6
BLACK_BACK_ROW = 0
BLACK_PAWN_ROW = 1

# File and rank mappings for algebraic notation
FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
RANKS = ['8', '7', '6', '5', '4', '3', '2', '1']

# Column indices for special positions
KING_COL = 4
QUEEN_COL = 3
KINGSIDE_ROOK_COL = 7
QUEENSIDE_ROOK_COL = 0

# Castling destination columns
KINGSIDE_KING_DEST = 6
QUEENSIDE_KING_DEST = 2
KINGSIDE_ROOK_DEST = 5
QUEENSIDE_ROOK_DEST = 3

class GameStatus(Enum):
    """Enum representing the current state of the game."""
    ACTIVE = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    DRAW_FIFTY_MOVE = auto()
    DRAW_THREEFOLD = auto()
    DRAW_INSUFFICIENT = auto()
    RESIGNED = auto()

class GameMode(Enum):
    """Enum representing game modes."""
    PLAYER_VS_AI = auto()
    PLAYER_VS_PLAYER = auto()

class Difficulty(Enum):
    """Enum representing AI difficulty levels."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3

# Direction vectors for piece movement
DIRECTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
    'NE': (-1, 1),
    'NW': (-1, -1),
    'SE': (1, 1),
    'SW': (1, -1)
}

# Knight move offsets
KNIGHT_MOVES = [
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    (1, -2), (1, 2), (2, -1), (2, 1)
]

# King move offsets
KING_MOVES = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

def pos_to_algebraic(position):
    """Convert board position (row, col) to algebraic notation."""
    row, col = position
    if 0 <= row < 8 and 0 <= col < 8:
        return FILES[col] + RANKS[row]
    return None

def algebraic_to_pos(notation):
    """Convert algebraic notation to board position (row, col)."""
    if len(notation) != 2:
        return None
    file_char, rank_char = notation[0].lower(), notation[1]
    if file_char in FILES and rank_char in RANKS:
        col = FILES.index(file_char)
        row = RANKS.index(rank_char)
        return (row, col)
    return None