from enum import Enum
from abc import ABC, abstractmethod
import numpy as np

class Color(Enum):
    WHITE = 1
    BLACK = -1

class PieceType(Enum):
    PAWN = 'P'
    KNIGHT = 'N'
    BISHOP = 'B'
    ROOK = 'R'
    QUEEN = 'Q'
    KING = 'K'

class Piece(ABC):
    """Abstract base class for all chess pieces."""
    
    def __init__(self, color, position):
        self.color = color
        self.position = position  # (row, col) tuple
        self.has_moved = False
        self.piece_type = None
        
    @abstractmethod
    def get_possible_moves(self, board):
        """Return all possible moves for this piece, not considering checks."""
        pass
    
    def __str__(self):
        color_char = 'w' if self.color == Color.WHITE else 'b'
        return f"{color_char}{self.piece_type.value}"
    
    def __repr__(self):
        return self.__str__()

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.PAWN
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        direction = -1 if self.color == Color.WHITE else 1
        
        # One square forward
        new_row = row + direction
        if 0 <= new_row < 8 and board[new_row, col] is None:
            moves.append((new_row, col))
            
            # Two squares forward from starting position
            if not self.has_moved:
                new_row_2 = row + 2 * direction
                if board[new_row_2, col] is None:
                    moves.append((new_row_2, col))
        
        # Diagonal captures
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
        
        # TODO: Add en passant logic later when we have game state
        
        return moves

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.KNIGHT
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        
        # All possible knight moves (L-shapes)
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for row_offset, col_offset in knight_moves:
            new_row = row + row_offset
            new_col = col + col_offset
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.BISHOP
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        
        # Diagonal directions: NE, NW, SE, SW
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for row_dir, col_dir in directions:
            for i in range(1, 8):
                new_row = row + i * row_dir
                new_col = col + i * col_dir
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board[new_row, new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
        
        return moves

class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.ROOK
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        
        # Horizontal and vertical directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for row_dir, col_dir in directions:
            for i in range(1, 8):
                new_row = row + i * row_dir
                new_col = col + i * col_dir
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board[new_row, new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
        
        return moves

class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.QUEEN
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        
        # All eight directions (combination of rook and bishop moves)
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Rook moves
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop moves
        ]
        
        for row_dir, col_dir in directions:
            for i in range(1, 8):
                new_row = row + i * row_dir
                new_col = col + i * col_dir
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board[new_row, new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
        
        return moves

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.piece_type = PieceType.KING
        
    def get_possible_moves(self, board):
        moves = []
        row, col = self.position
        
        # All eight adjacent squares
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for row_offset, col_offset in king_moves:
            new_row = row + row_offset
            new_col = col + col_offset
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        # TODO: Add castling logic later when we have game state
        
        return moves