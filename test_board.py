import unittest
from core.board import Board
from core.piece import *

class TestBoard(unittest.TestCase):
    
    def setUp(self):
        """Set up a board for testing."""
        self.board = Board()
    
    def test_initial_setup(self):
        """Test initial board setup."""
        # Test white pieces
        self.assertIsInstance(self.board.get_piece((7, 0)), Rook)
        self.assertIsInstance(self.board.get_piece((7, 1)), Knight)
        self.assertIsInstance(self.board.get_piece((7, 2)), Bishop)
        self.assertIsInstance(self.board.get_piece((7, 3)), Queen)
        self.assertIsInstance(self.board.get_piece((7, 4)), King)
        
        # Test pawns
        for col in range(8):
            self.assertIsInstance(self.board.get_piece((6, col)), Pawn)
            self.assertEqual(self.board.get_piece((6, col)).color, Color.WHITE)
            self.assertIsInstance(self.board.get_piece((1, col)), Pawn)
            self.assertEqual(self.board.get_piece((1, col)).color, Color.BLACK)
            
        # Test empty squares
        for row in range(2, 6):
            for col in range(8):
                self.assertIsNone(self.board.get_piece((row, col)))
    
    def test_move_piece(self):
        """Test basic piece movement."""
        # Move white pawn e2 to e4
        result = self.board.move_piece((6, 4), (4, 4))
        self.assertIsNone(result)  # No capture
        self.assertIsNone(self.board.get_piece((6, 4)))
        self.assertIsInstance(self.board.get_piece((4, 4)), Pawn)
        self.assertTrue(self.board.get_piece((4, 4)).has_moved)
        
    def test_invalid_move(self):
        """Test invalid move is rejected."""
        # Try to move pawn diagonally without capture
        result = self.board.move_piece((6, 4), (5, 5))
        self.assertFalse(result)
        self.assertIsInstance(self.board.get_piece((6, 4)), Pawn)
        self.assertIsNone(self.board.get_piece((5, 5)))
        
    def test_capture(self):
        """Test piece capture."""
        self.board.clear()
        white_pawn = Pawn(Color.WHITE, (4, 4))
        black_pawn = Pawn(Color.BLACK, (3, 5))
        self.board.set_piece((4, 4), white_pawn)
        self.board.set_piece((3, 5), black_pawn)
        
        captured = self.board.move_piece((4, 4), (3, 5))
        self.assertEqual(captured, black_pawn)
        self.assertIsNone(self.board.get_piece((4, 4)))
        self.assertEqual(self.board.get_piece((3, 5)), white_pawn)
        
    def test_get_all_pieces(self):
        """Test getting all pieces."""
        pieces = self.board.get_all_pieces()
        self.assertEqual(len(pieces), 32)  # All pieces on starting position
        
        white_pieces = self.board.get_all_pieces(Color.WHITE)
        self.assertEqual(len(white_pieces), 16)
        
        black_pieces = self.board.get_all_pieces(Color.BLACK)
        self.assertEqual(len(black_pieces), 16)
        
    def test_find_king(self):
        """Test finding kings."""
        white_king = self.board.find_king(Color.WHITE)
        self.assertIsNotNone(white_king)
        self.assertEqual(white_king.position, (7, 4))
        
        black_king = self.board.find_king(Color.BLACK)
        self.assertIsNotNone(black_king)
        self.assertEqual(black_king.position, (0, 4))
        
    def test_is_square_attacked(self):
        """Test square attack detection."""
        self.board.clear()
        # Place a white rook
        rook = Rook(Color.WHITE, (4, 4))
        self.board.set_piece((4, 4), rook)
        
        # Check attacked squares
        self.assertTrue(self.board.is_square_attacked((4, 7), Color.WHITE))  # Same rank
        self.assertTrue(self.board.is_square_attacked((7, 4), Color.WHITE))  # Same file
        self.assertFalse(self.board.is_square_attacked((5, 5), Color.WHITE))  # Diagonal
        
    def test_is_in_check(self):
        """Test check detection."""
        self.board.clear()
        # Set up a check position
        white_king = King(Color.WHITE, (7, 4))
        black_rook = Rook(Color.BLACK, (7, 0))
        self.board.set_piece((7, 4), white_king)
        self.board.set_piece((7, 0), black_rook)
        
        self.assertTrue(self.board.is_in_check(Color.WHITE))
        self.assertFalse(self.board.is_in_check(Color.BLACK))
        
    def test_board_copy(self):
        """Test board copying."""
        copy = self.board.copy()
        
        # Verify it's a different board
        self.assertIsNot(copy, self.board)
        self.assertIsNot(copy.board, self.board.board)
        
        # Verify pieces are copied
        for row in range(8):
            for col in range(8):
                original = self.board.get_piece((row, col))
                copied = copy.get_piece((row, col))
                if original:
                    self.assertIsNot(original, copied)
                    self.assertEqual(type(original), type(copied))
                    self.assertEqual(original.color, copied.color)
                    self.assertEqual(original.position, copied.position)
                    
    def test_board_string_representation(self):
        """Test board string output."""
        board_str = str(self.board)
        self.assertIn('a b c d e f g h', board_str)
        self.assertIn('8', board_str)
        self.assertIn('1', board_str)

if __name__ == '__main__':
    unittest.main()