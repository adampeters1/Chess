import numpy as np
from copy import deepcopy
from .piece import *

class Board:
    """Chess board representation and management."""
    
    def __init__(self):
        self.board = np.empty((8, 8), dtype=object)
        self.setup_initial_position()
        
    def setup_initial_position(self):
        """Set up the standard chess starting position."""
        # Place pawns
        for col in range(8):
            self.board[1, col] = Pawn(Color.BLACK, (1, col))
            self.board[6, col] = Pawn(Color.WHITE, (6, col))
        
        # Place other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        for col, piece_class in enumerate(piece_order):
            self.board[0, col] = piece_class(Color.BLACK, (0, col))
            self.board[7, col] = piece_class(Color.WHITE, (7, col))
    
    def get_piece(self, position):
        """Get piece at given position."""
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row, col]
        return None
    
    def set_piece(self, position, piece):
        """Set piece at given position."""
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row, col] = piece
            if piece:
                piece.position = position
    
    def move_piece(self, from_pos, to_pos):
        """Move a piece from one position to another."""
        piece = self.get_piece(from_pos)
        if piece is None:
            return False
        
        # Check if the move is in the piece's possible moves
        possible_moves = piece.get_possible_moves(self.board)
        if to_pos not in possible_moves:
            return False
        
        # Capture piece at destination if exists
        captured = self.get_piece(to_pos)
        
        # Make the move
        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)
        piece.has_moved = True
        
        return captured
    
    def get_all_pieces(self, color=None):
        """Get all pieces on the board, optionally filtered by color."""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece and (color is None or piece.color == color):
                    pieces.append(piece)
        return pieces
    
    def find_king(self, color):
        """Find the king of the specified color."""
        for piece in self.get_all_pieces(color):
            if piece.piece_type == PieceType.KING:
                return piece
        return None
    
    def is_square_attacked(self, square, by_color):
        """Check if a square is attacked by any piece of the given color."""
        for piece in self.get_all_pieces(by_color):
            if square in piece.get_possible_moves(self.board):
                return True
        return False
    
    def is_in_check(self, color):
        """Check if the king of the given color is in check."""
        king = self.find_king(color)
        if king:
            enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
            return self.is_square_attacked(king.position, enemy_color)
        return False
    
    def copy(self):
        """Create a deep copy of the board."""
        new_board = Board()
        new_board.board = np.empty((8, 8), dtype=object)
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece:
                    # Create a new piece of the same type
                    piece_class = type(piece)
                    new_piece = piece_class(piece.color, (row, col))
                    new_piece.has_moved = piece.has_moved
                    new_board.board[row, col] = new_piece
        
        return new_board
    
    def clear(self):
        """Clear the board."""
        self.board = np.empty((8, 8), dtype=object)
    
    def __str__(self):
        """String representation of the board."""
        result = "  a b c d e f g h\n"
        for row in range(8):
            result += f"{8-row} "
            for col in range(8):
                piece = self.board[row, col]
                if piece:
                    result += str(piece) + " "
                else:
                    result += ". "
            result += f"{8-row}\n"
        result += "  a b c d e f g h"
        return result