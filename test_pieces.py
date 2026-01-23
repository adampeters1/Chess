import unittest
import numpy as np
from core.piece import *

class TestPieces(unittest.TestCase):
    
    def setUp(self):
        """Set up an empty board for testing."""
        self.board = np.empty((8, 8), dtype=object)
    
    def test_pawn_initial_moves(self):
        """Test pawn can move 1 or 2 squares from starting position."""
        pawn = Pawn(Color.WHITE, (6, 4))  # e2
        moves = pawn.get_possible_moves(self.board)
        expected = [(5, 4), (4, 4)]  # e3, e4
        self.assertEqual(sorted(moves), sorted(expected))
        
    def test_pawn_blocked(self):
        """Test pawn cannot move when blocked."""
        pawn = Pawn(Color.WHITE, (6, 4))
        self.board[5, 4] = Pawn(Color.BLACK, (5, 4))
        moves = pawn.get_possible_moves(self.board)
        self.assertEqual(moves, [])
        
    def test_pawn_capture(self):
        """Test pawn diagonal capture."""
        pawn = Pawn(Color.WHITE, (6, 4))  # e2
        self.board[5, 3] = Pawn(Color.BLACK, (5, 3))  # d3
        self.board[5, 5] = Pawn(Color.BLACK, (5, 5))  # f3
        moves = pawn.get_possible_moves(self.board)
        self.assertIn((5, 3), moves)  # Can capture on d3
        self.assertIn((5, 5), moves)  # Can capture on f3
        
    def test_pawn_cannot_capture_own_piece(self):
        """Test pawn cannot capture own piece."""
        pawn = Pawn(Color.WHITE, (6, 4))
        self.board[5, 3] = Pawn(Color.WHITE, (5, 3))
        moves = pawn.get_possible_moves(self.board)
        self.assertNotIn((5, 3), moves)
        
    def test_knight_moves(self):
        """Test knight L-shaped moves."""
        knight = Knight(Color.WHITE, (4, 4))  # e4
        moves = knight.get_possible_moves(self.board)
        expected = [
            (2, 3), (2, 5),  # c6, g6
            (3, 2), (3, 6),  # b5, h5
            (5, 2), (5, 6),  # b3, h3
            (6, 3), (6, 5)   # c2, g2
        ]
        self.assertEqual(sorted(moves), sorted(expected))
        
    def test_knight_edge_moves(self):
        """Test knight moves from edge of board."""
        knight = Knight(Color.WHITE, (0, 0))  # a8
        moves = knight.get_possible_moves(self.board)
        expected = [(1, 2), (2, 1)]
        self.assertEqual(sorted(moves), sorted(expected))
        
    def test_bishop_moves(self):
        """Test bishop diagonal moves."""
        bishop = Bishop(Color.WHITE, (4, 4))  # e4
        moves = bishop.get_possible_moves(self.board)
        self.assertEqual(len(moves), 13)  # All diagonal squares from e4
        
    def test_bishop_blocked(self):
        """Test bishop blocked by pieces."""
        bishop = Bishop(Color.WHITE, (4, 4))
        self.board[3, 3] = Pawn(Color.WHITE, (3, 3))  # Block one diagonal
        moves = bishop.get_possible_moves(self.board)
        self.assertNotIn((2, 2), moves)  # Can't go past own piece
        self.assertNotIn((3, 3), moves)  # Can't capture own piece
        
    def test_rook_moves(self):
        """Test rook horizontal and vertical moves."""
        rook = Rook(Color.WHITE, (4, 4))  # e4
        moves = rook.get_possible_moves(self.board)
        self.assertEqual(len(moves), 14)  # All horizontal and vertical squares
        
    def test_queen_moves(self):
        """Test queen combines rook and bishop moves."""
        queen = Queen(Color.WHITE, (4, 4))  # e4
        moves = queen.get_possible_moves(self.board)
        self.assertEqual(len(moves), 27)  # All horizontal, vertical, and diagonal squares
        
    def test_king_moves(self):
        """Test king one square moves."""
        king = King(Color.WHITE, (4, 4))  # e4
        moves = king.get_possible_moves(self.board)
        expected = [
            (3, 3), (3, 4), (3, 5),
            (4, 3),         (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        self.assertEqual(sorted(moves), sorted(expected))
        
    def test_king_corner_moves(self):
        """Test king moves from corner."""
        king = King(Color.WHITE, (0, 0))  # a8
        moves = king.get_possible_moves(self.board)
        expected = [(0, 1), (1, 0), (1, 1)]
        self.assertEqual(sorted(moves), sorted(expected))

if __name__ == '__main__':
    unittest.main()