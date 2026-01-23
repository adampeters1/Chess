import unittest
from core.game import Game, Move
from core.board import Board
from core.piece import Color, PieceType, Pawn, Rook, Knight, Bishop, Queen, King
from core.constants import GameStatus, GameMode, Difficulty

class TestGame(unittest.TestCase):
    
    def setUp(self):
        """Set up a game for testing."""
        self.game = Game()
    
    def test_initial_state(self):
        """Test initial game state."""
        self.assertEqual(self.game.current_player, Color.WHITE)
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertEqual(len(self.game.move_history), 0)
        self.assertIsNone(self.game.en_passant_target)
        self.assertEqual(self.game.fullmove_number, 1)
        
    def test_switch_player(self):
        """Test player switching."""
        self.assertEqual(self.game.current_player, Color.WHITE)
        self.game.switch_player()
        self.assertEqual(self.game.current_player, Color.BLACK)
        self.game.switch_player()
        self.assertEqual(self.game.current_player, Color.WHITE)
        
    def test_legal_moves_basic(self):
        """Test basic legal move generation."""
        # Get legal moves for white pawn on e2
        pawn = self.game.board.get_piece((6, 4))
        moves = self.game.get_legal_moves(pawn)
        self.assertIn((5, 4), moves)  # e3
        self.assertIn((4, 4), moves)  # e4
        
    def test_legal_moves_blocked(self):
        """Test that blocked moves are not legal."""
        # Knight on b1 should have limited moves
        knight = self.game.board.get_piece((7, 1))
        moves = self.game.get_legal_moves(knight)
        self.assertEqual(len(moves), 2)  # a3 and c3
        
    def test_make_move(self):
        """Test making a basic move."""
        result = self.game.make_move((6, 4), (4, 4))  # e2-e4
        self.assertTrue(result)
        self.assertIsNone(self.game.board.get_piece((6, 4)))
        self.assertIsInstance(self.game.board.get_piece((4, 4)), Pawn)
        self.assertEqual(self.game.current_player, Color.BLACK)
        self.assertEqual(len(self.game.move_history), 1)
        
    def test_make_invalid_move(self):
        """Test that invalid moves are rejected."""
        result = self.game.make_move((6, 4), (3, 4))  # e2-e5 (too far)
        self.assertFalse(result)
        self.assertEqual(self.game.current_player, Color.WHITE)
        
    def test_cannot_move_wrong_color(self):
        """Test that you can't move opponent's pieces."""
        result = self.game.make_move((1, 4), (3, 4))  # Try to move black pawn
        self.assertFalse(result)
        
    def test_cannot_move_into_check(self):
        """Test that moves leaving king in check are illegal."""
        self.game.board.clear()
        
        # Set up position where moving the bishop would expose king to check
        white_king = King(Color.WHITE, (7, 4))
        white_bishop = Bishop(Color.WHITE, (7, 3))
        black_rook = Rook(Color.BLACK, (7, 0))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 3), white_bishop)
        self.game.board.set_piece((7, 0), black_rook)
        
        # Bishop cannot move because it's pinned
        bishop = self.game.board.get_piece((7, 3))
        moves = self.game.get_legal_moves(bishop)
        self.assertEqual(len(moves), 0)
        
    def test_must_block_check(self):
        """Test that when in check, only blocking moves are legal."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_rook = Rook(Color.WHITE, (6, 0))
        black_rook = Rook(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((6, 0), white_rook)
        self.game.board.set_piece((0, 4), black_rook)
        
        # White is in check
        self.assertTrue(self.game.board.is_in_check(Color.WHITE))
        
        # Rook should be able to block
        rook = self.game.board.get_piece((6, 0))
        moves = self.game.get_legal_moves(rook)
        self.assertIn((6, 4), moves)  # Block check
        
    def test_en_passant(self):
        """Test en passant capture."""
        self.game.board.clear()
        
        white_pawn = Pawn(Color.WHITE, (3, 4))  # e5
        white_pawn.has_moved = True
        black_pawn = Pawn(Color.BLACK, (1, 3))  # d7
        black_king = King(Color.BLACK, (0, 0))
        white_king = King(Color.WHITE, (7, 4))
        
        self.game.board.set_piece((3, 4), white_pawn)
        self.game.board.set_piece((1, 3), black_pawn)
        self.game.board.set_piece((0, 0), black_king)
        self.game.board.set_piece((7, 4), white_king)
        
        # White to move, then black moves pawn two squares
        self.game.current_player = Color.BLACK
        self.game.make_move((1, 3), (3, 3))  # d7-d5
        
        # Now white can capture en passant
        self.assertEqual(self.game.en_passant_target, (2, 3))  # d6
        white_pawn = self.game.board.get_piece((3, 4))
        moves = self.game.get_legal_moves(white_pawn)
        self.assertIn((2, 3), moves)  # en passant capture
        
    def test_castling_kingside(self):
        """Test kingside castling."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_rook = Rook(Color.WHITE, (7, 7))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 7), white_rook)
        self.game.board.set_piece((0, 4), black_king)
        
        # Check castling is available
        king = self.game.board.get_piece((7, 4))
        moves = self.game.get_legal_moves(king)
        self.assertIn((7, 6), moves)  # Kingside castle
        
        # Execute castling
        result = self.game.make_move((7, 4), (7, 6))
        self.assertTrue(result)
        self.assertIsInstance(self.game.board.get_piece((7, 6)), King)
        self.assertIsInstance(self.game.board.get_piece((7, 5)), Rook)
        
    def test_castling_queenside(self):
        """Test queenside castling."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_rook = Rook(Color.WHITE, (7, 0))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 0), white_rook)
        self.game.board.set_piece((0, 4), black_king)
        
        king = self.game.board.get_piece((7, 4))
        moves = self.game.get_legal_moves(king)
        self.assertIn((7, 2), moves)  # Queenside castle
        
    def test_no_castling_through_check(self):
        """Test that castling through check is not allowed."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_rook = Rook(Color.WHITE, (7, 7))
        black_rook = Rook(Color.BLACK, (0, 5))  # Attacks f1
        black_king = King(Color.BLACK, (0, 0))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 7), white_rook)
        self.game.board.set_piece((0, 5), black_rook)
        self.game.board.set_piece((0, 0), black_king)
        
        king = self.game.board.get_piece((7, 4))
        moves = self.game.get_legal_moves(king)
        self.assertNotIn((7, 6), moves)  # Cannot castle through check
        
    def test_no_castling_after_king_moved(self):
        """Test that castling is not allowed after king has moved."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_king.has_moved = True
        white_rook = Rook(Color.WHITE, (7, 7))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 7), white_rook)
        self.game.board.set_piece((0, 4), black_king)
        
        king = self.game.board.get_piece((7, 4))
        moves = self.game.get_legal_moves(king)
        self.assertNotIn((7, 6), moves)
        
    def test_pawn_promotion(self):
        """Test pawn promotion."""
        self.game.board.clear()
        
        white_pawn = Pawn(Color.WHITE, (1, 4))  # e7
        white_pawn.has_moved = True
        white_king = King(Color.WHITE, (7, 4))
        black_king = King(Color.BLACK, (0, 0))
        
        self.game.board.set_piece((1, 4), white_pawn)
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((0, 0), black_king)
        
        # Promote to queen
        result = self.game.make_move((1, 4), (0, 4), PieceType.QUEEN)
        self.assertTrue(result)
        promoted_piece = self.game.board.get_piece((0, 4))
        self.assertIsInstance(promoted_piece, Queen)
        
    def test_checkmate(self):
        """Test checkmate detection."""
        self.game.board.clear()
        
        # Fool's mate position
        white_king = King(Color.WHITE, (7, 4))
        white_queen = Queen(Color.WHITE, (4, 7))  # Qh4
        black_king = King(Color.BLACK, (0, 4))
        black_pawn_f = Pawn(Color.BLACK, (2, 5))  # f6
        black_pawn_g = Pawn(Color.BLACK, (3, 6))  # g5
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((4, 7), white_queen)
        self.game.board.set_piece((0, 4), black_king)
        self.game.board.set_piece((2, 5), black_pawn_f)
        self.game.board.set_piece((3, 6), black_pawn_g)
        
        self.game.current_player = Color.WHITE
        # Queen delivers checkmate
        result = self.game.make_move((4, 7), (3, 5))  # Qf5 mate-ish setup
        
        # Set up actual checkmate
        self.game.board.clear()
        black_king = King(Color.BLACK, (0, 4))
        white_queen = Queen(Color.WHITE, (1, 4))
        white_king = King(Color.WHITE, (2, 4))
        
        self.game.board.set_piece((0, 4), black_king)
        self.game.board.set_piece((1, 4), white_queen)
        self.game.board.set_piece((2, 4), white_king)
        
        self.game.current_player = Color.BLACK
        self.game._update_game_status()
        
        self.assertEqual(self.game.status, GameStatus.CHECKMATE)
        
    def test_stalemate(self):
        """Test stalemate detection."""
        self.game.board.clear()
        
        # Classic stalemate position
        black_king = King(Color.BLACK, (0, 0))
        white_king = King(Color.WHITE, (2, 1))
        white_queen = Queen(Color.WHITE, (1, 2))
        
        self.game.board.set_piece((0, 0), black_king)
        self.game.board.set_piece((2, 1), white_king)
        self.game.board.set_piece((1, 2), white_queen)
        
        self.game.current_player = Color.BLACK
        self.game._update_game_status()
        
        self.assertEqual(self.game.status, GameStatus.STALEMATE)
        
    def test_undo_move(self):
        """Test undo functionality."""
        # Make a move
        self.game.make_move((6, 4), (4, 4))  # e2-e4
        self.assertEqual(self.game.current_player, Color.BLACK)
        
        # Undo the move
        result = self.game.undo_move()
        self.assertTrue(result)
        self.assertEqual(self.game.current_player, Color.WHITE)
        self.assertIsInstance(self.game.board.get_piece((6, 4)), Pawn)
        self.assertIsNone(self.game.board.get_piece((4, 4)))
        
    def test_undo_capture(self):
        """Test undo with capture."""
        self.game.board.clear()
        
        white_pawn = Pawn(Color.WHITE, (4, 4))
        white_pawn.has_moved = True
        black_pawn = Pawn(Color.BLACK, (3, 5))
        black_pawn.has_moved = True
        white_king = King(Color.WHITE, (7, 4))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((4, 4), white_pawn)
        self.game.board.set_piece((3, 5), black_pawn)
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((0, 4), black_king)
        
        # Capture
        self.game.make_move((4, 4), (3, 5))
        self.assertIsNone(self.game.board.get_piece((4, 4)))
        
        # Undo
        self.game.undo_move()
        self.assertIsInstance(self.game.board.get_piece((4, 4)), Pawn)
        self.assertIsInstance(self.game.board.get_piece((3, 5)), Pawn)
        self.assertEqual(self.game.board.get_piece((3, 5)).color, Color.BLACK)
        
    def test_undo_castling(self):
        """Test undo castling."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_rook = Rook(Color.WHITE, (7, 7))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((7, 7), white_rook)
        self.game.board.set_piece((0, 4), black_king)
        
        # Castle kingside
        self.game.make_move((7, 4), (7, 6))
        
        # Undo castling
        self.game.undo_move()
        self.assertIsInstance(self.game.board.get_piece((7, 4)), King)
        self.assertIsInstance(self.game.board.get_piece((7, 7)), Rook)
        self.assertIsNone(self.game.board.get_piece((7, 6)))
        self.assertIsNone(self.game.board.get_piece((7, 5)))
        self.assertFalse(self.game.board.get_piece((7, 4)).has_moved)
        self.assertFalse(self.game.board.get_piece((7, 7)).has_moved)
        
    def test_insufficient_material_king_vs_king(self):
        """Test draw by insufficient material - K vs K."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((0, 4), black_king)
        
        self.game._update_game_status()
        self.assertEqual(self.game.status, GameStatus.DRAW_INSUFFICIENT)
        
    def test_insufficient_material_king_bishop_vs_king(self):
        """Test draw by insufficient material - K+B vs K."""
        self.game.board.clear()
        
        white_king = King(Color.WHITE, (7, 4))
        white_bishop = Bishop(Color.WHITE, (4, 4))
        black_king = King(Color.BLACK, (0, 4))
        
        self.game.board.set_piece((7, 4), white_king)
        self.game.board.set_piece((4, 4), white_bishop)
        self.game.board.set_piece((0, 4), black_king)
        
        self.game._update_game_status()
        self.assertEqual(self.game.status, GameStatus.DRAW_INSUFFICIENT)
        
    def test_game_reset(self):
        """Test game reset functionality."""
        self.game.make_move((6, 4), (4, 4))
        self.game.make_move((1, 4), (3, 4))
        
        self.game.reset()
        
        self.assertEqual(self.game.current_player, Color.WHITE)
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertEqual(len(self.game.move_history), 0)
        self.assertIsInstance(self.game.board.get_piece((6, 4)), Pawn)
        
    def test_is_game_over(self):
        """Test is_game_over method."""
        self.assertFalse(self.game.is_game_over())
        
        self.game.status = GameStatus.CHECKMATE
        self.assertTrue(self.game.is_game_over())
        
        self.game.status = GameStatus.STALEMATE
        self.assertTrue(self.game.is_game_over())
        
    def test_get_winner(self):
        """Test get_winner method."""
        self.assertIsNone(self.game.get_winner())
        
        # Simulate checkmate where black is checkmated
        self.game.status = GameStatus.CHECKMATE
        self.game.current_player = Color.BLACK  # Black to move but checkmated
        self.assertEqual(self.game.get_winner(), Color.WHITE)

if __name__ == '__main__':
    unittest.main()