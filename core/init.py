"""
Chess Game Core Module

This module contains the core chess game logic including:
- Piece definitions and movement rules
- Board representation and management
- Game state and rule enforcement
- Constants and enumerations
"""

from .piece import (
    Color,
    PieceType,
    Piece,
    Pawn,
    Knight,
    Bishop,
    Rook,
    Queen,
    King
)

from .board import Board

from .game import (
    Game,
    Move
)

from .constants import (
    BOARD_SIZE,
    BOARD_ROWS,
    BOARD_COLS,
    GameStatus,
    GameMode,
    Difficulty,
    pos_to_algebraic,
    algebraic_to_pos,
    FILES,
    RANKS
)

__all__ = [
    # Piece classes
    'Color',
    'PieceType',
    'Piece',
    'Pawn',
    'Knight',
    'Bishop',
    'Rook',
    'Queen',
    'King',
    
    # Board
    'Board',
    
    # Game
    'Game',
    'Move',
    
    # Constants and utilities
    'BOARD_SIZE',
    'BOARD_ROWS',
    'BOARD_COLS',
    'GameStatus',
    'GameMode',
    'Difficulty',
    'pos_to_algebraic',
    'algebraic_to_pos',
    'FILES',
    'RANKS'
]

__version__ = '0.1.0'