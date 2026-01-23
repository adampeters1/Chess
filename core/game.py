from collections import deque
from copy import deepcopy
from .board import Board
from .piece import Color, PieceType, Pawn, Rook, Knight, Bishop, Queen, King
from .constants import (
    GameStatus, GameMode, Difficulty,
    KING_COL, KINGSIDE_ROOK_COL, QUEENSIDE_ROOK_COL,
    KINGSIDE_KING_DEST, QUEENSIDE_KING_DEST,
    KINGSIDE_ROOK_DEST, QUEENSIDE_ROOK_DEST,
    WHITE_BACK_ROW, BLACK_BACK_ROW
)

class Move:
    """Represents a chess move with all relevant information."""
    
    def __init__(self, from_pos, to_pos, piece, captured=None, 
                 promotion_piece=None, is_castling=False, is_en_passant=False,
                 castling_side=None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured = captured
        self.promotion_piece = promotion_piece
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.castling_side = castling_side  # 'kingside' or 'queenside'
        self.piece_had_moved = piece.has_moved if piece else False
        
    def __str__(self):
        from constants import pos_to_algebraic
        return f"{self.piece} {pos_to_algebraic(self.from_pos)}->{pos_to_algebraic(self.to_pos)}"
    
    def __repr__(self):
        return self.__str__()

class Game:
    """Main game class that manages chess game state and rules."""
    
    def __init__(self, mode=GameMode.PLAYER_VS_AI, difficulty=Difficulty.INTERMEDIATE):
        self.board = Board()
        self.current_player = Color.WHITE
        self.status = GameStatus.ACTIVE
        self.mode = mode
        self.difficulty = difficulty
        self.move_history = deque()
        self.en_passant_target = None  # Square where en passant capture is possible
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_number = 1
        
    def reset(self):
        """Reset the game to initial state."""
        self.board = Board()
        self.current_player = Color.WHITE
        self.status = GameStatus.ACTIVE
        self.move_history.clear()
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
    def switch_player(self):
        """Switch the current player."""
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
    def get_legal_moves(self, piece):
        """Get all legal moves for a piece, filtering out moves that leave king in check."""
        if piece is None or piece.color != self.current_player:
            return []
        
        possible_moves = piece.get_possible_moves(self.board.board)
        legal_moves = []
        
        for move in possible_moves:
            if self._is_move_legal(piece, move):
                legal_moves.append(move)
        
        # Add castling moves for king
        if piece.piece_type == PieceType.KING:
            castling_moves = self._get_castling_moves(piece)
            legal_moves.extend(castling_moves)
            
        # Add en passant moves for pawn
        if piece.piece_type == PieceType.PAWN:
            en_passant_move = self._get_en_passant_move(piece)
            if en_passant_move:
                legal_moves.append(en_passant_move)
        
        return legal_moves
    
    def _is_move_legal(self, piece, to_pos):
        """Check if a move is legal (doesn't leave own king in check)."""
        # Create a copy of the board to simulate the move
        test_board = self.board.copy()
        from_pos = piece.position
        
        # Simulate the move
        test_board.set_piece(to_pos, test_board.get_piece(from_pos))
        test_board.set_piece(from_pos, None)
        test_board.get_piece(to_pos).position = to_pos
        
        # Check if king is in check after the move
        return not test_board.is_in_check(piece.color)
    
    def _get_castling_moves(self, king):
        """Get available castling moves for the king."""
        castling_moves = []
        
        if king.has_moved or self.board.is_in_check(king.color):
            return castling_moves
        
        row = WHITE_BACK_ROW if king.color == Color.WHITE else BLACK_BACK_ROW
        enemy_color = Color.BLACK if king.color == Color.WHITE else Color.WHITE
        
        # Kingside castling
        kingside_rook = self.board.get_piece((row, KINGSIDE_ROOK_COL))
        if (kingside_rook and 
            kingside_rook.piece_type == PieceType.ROOK and 
            not kingside_rook.has_moved):
            # Check if squares between king and rook are empty
            if (self.board.get_piece((row, 5)) is None and 
                self.board.get_piece((row, 6)) is None):
                # Check if king doesn't pass through or land on attacked square
                if (not self.board.is_square_attacked((row, 5), enemy_color) and
                    not self.board.is_square_attacked((row, 6), enemy_color)):
                    castling_moves.append((row, KINGSIDE_KING_DEST))
        
        # Queenside castling
        queenside_rook = self.board.get_piece((row, QUEENSIDE_ROOK_COL))
        if (queenside_rook and 
            queenside_rook.piece_type == PieceType.ROOK and 
            not queenside_rook.has_moved):
            # Check if squares between king and rook are empty
            if (self.board.get_piece((row, 1)) is None and
                self.board.get_piece((row, 2)) is None and 
                self.board.get_piece((row, 3)) is None):
                # Check if king doesn't pass through or land on attacked square
                if (not self.board.is_square_attacked((row, 2), enemy_color) and
                    not self.board.is_square_attacked((row, 3), enemy_color)):
                    castling_moves.append((row, QUEENSIDE_KING_DEST))
        
        return castling_moves
    
    def _get_en_passant_move(self, pawn):
        """Get en passant capture move if available."""
        if self.en_passant_target is None:
            return None
        
        row, col = pawn.position
        target_row, target_col = self.en_passant_target
        direction = -1 if pawn.color == Color.WHITE else 1
        
        # Check if pawn can capture en passant
        if row + direction == target_row and abs(col - target_col) == 1:
            # Verify move is legal (doesn't leave king in check)
            test_board = self.board.copy()
            test_board.set_piece(self.en_passant_target, test_board.get_piece(pawn.position))
            test_board.set_piece(pawn.position, None)
            test_board.set_piece((row, target_col), None)  # Remove captured pawn
            test_board.get_piece(self.en_passant_target).position = self.en_passant_target
            
            if not test_board.is_in_check(pawn.color):
                return self.en_passant_target
        
        return None
    
    def make_move(self, from_pos, to_pos, promotion_piece_type=None):
        """Execute a move and update game state."""
        piece = self.board.get_piece(from_pos)
        
        if piece is None or piece.color != self.current_player:
            return False
        
        legal_moves = self.get_legal_moves(piece)
        if to_pos not in legal_moves:
            return False
        
        captured = self.board.get_piece(to_pos)
        is_castling = False
        is_en_passant = False
        castling_side = None
        
        # Handle castling
        if piece.piece_type == PieceType.KING and abs(to_pos[1] - from_pos[1]) == 2:
            is_castling = True
            castling_side = 'kingside' if to_pos[1] > from_pos[1] else 'queenside'
            self._execute_castling(piece, to_pos)
        # Handle en passant
        elif (piece.piece_type == PieceType.PAWN and 
              to_pos == self.en_passant_target):
            is_en_passant = True
            captured = self._execute_en_passant(piece, to_pos)
        # Handle normal move
        else:
            self.board.set_piece(to_pos, piece)
            self.board.set_piece(from_pos, None)
            piece.position = to_pos
        
        # Handle pawn promotion
        promotion_piece = None
        if piece.piece_type == PieceType.PAWN:
            promotion_row = 0 if piece.color == Color.WHITE else 7
            if to_pos[0] == promotion_row:
                promotion_piece = self._promote_pawn(to_pos, promotion_piece_type)
        
        # Update en passant target
        self._update_en_passant_target(piece, from_pos, to_pos)
        
        # Record move in history
        move = Move(
            from_pos=from_pos,
            to_pos=to_pos,
            piece=piece,
            captured=captured,
            promotion_piece=promotion_piece,
            is_castling=is_castling,
            is_en_passant=is_en_passant,
            castling_side=castling_side
        )
        self.move_history.append(move)
        
        # Update move counters
        piece.has_moved = True
        if piece.piece_type == PieceType.PAWN or captured:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        if self.current_player == Color.BLACK:
            self.fullmove_number += 1
        
        # Switch player and update game status
        self.switch_player()
        self._update_game_status()
        
        return True
    
    def _execute_castling(self, king, to_pos):
        """Execute a castling move."""
        from_pos = king.position
        row = from_pos[0]
        
        # Move king
        self.board.set_piece(to_pos, king)
        self.board.set_piece(from_pos, None)
        king.position = to_pos
        
        # Move rook
        if to_pos[1] == KINGSIDE_KING_DEST:  # Kingside
            rook = self.board.get_piece((row, KINGSIDE_ROOK_COL))
            self.board.set_piece((row, KINGSIDE_ROOK_DEST), rook)
            self.board.set_piece((row, KINGSIDE_ROOK_COL), None)
            rook.position = (row, KINGSIDE_ROOK_DEST)
            rook.has_moved = True
        else:  # Queenside
            rook = self.board.get_piece((row, QUEENSIDE_ROOK_COL))
            self.board.set_piece((row, QUEENSIDE_ROOK_DEST), rook)
            self.board.set_piece((row, QUEENSIDE_ROOK_COL), None)
            rook.position = (row, QUEENSIDE_ROOK_DEST)
            rook.has_moved = True
    
    def _execute_en_passant(self, pawn, to_pos):
        """Execute an en passant capture."""
        from_pos = pawn.position
        captured_pawn_pos = (from_pos[0], to_pos[1])
        captured = self.board.get_piece(captured_pawn_pos)
        
        self.board.set_piece(to_pos, pawn)
        self.board.set_piece(from_pos, None)
        self.board.set_piece(captured_pawn_pos, None)
        pawn.position = to_pos
        
        return captured
    
    def _promote_pawn(self, position, piece_type=None):
        """Promote a pawn to another piece."""
        pawn = self.board.get_piece(position)
        color = pawn.color
        
        # Default to queen if no piece type specified
        if piece_type is None:
            piece_type = PieceType.QUEEN
        
        piece_classes = {
            PieceType.QUEEN: Queen,
            PieceType.ROOK: Rook,
            PieceType.BISHOP: Bishop,
            PieceType.KNIGHT: Knight
        }
        
        piece_class = piece_classes.get(piece_type, Queen)
        new_piece = piece_class(color, position)
        new_piece.has_moved = True
        self.board.set_piece(position, new_piece)
        
        return new_piece
    
    def _update_en_passant_target(self, piece, from_pos, to_pos):
        """Update the en passant target square."""
        self.en_passant_target = None
        
        if piece.piece_type == PieceType.PAWN:
            # Check if pawn moved two squares
            if abs(to_pos[0] - from_pos[0]) == 2:
                # Set en passant target to the square the pawn passed through
                en_passant_row = (from_pos[0] + to_pos[0]) // 2
                self.en_passant_target = (en_passant_row, to_pos[1])
    
    def _update_game_status(self):
        """Update the game status based on current board state."""
        # Check if current player has any legal moves
        has_legal_moves = False
        for piece in self.board.get_all_pieces(self.current_player):
            if self.get_legal_moves(piece):
                has_legal_moves = True
                break
        
        in_check = self.board.is_in_check(self.current_player)
        
        if not has_legal_moves:
            if in_check:
                self.status = GameStatus.CHECKMATE
            else:
                self.status = GameStatus.STALEMATE
        elif in_check:
            self.status = GameStatus.CHECK
        elif self.halfmove_clock >= 100:  # 50 moves = 100 half-moves
            self.status = GameStatus.DRAW_FIFTY_MOVE
        elif self._is_insufficient_material():
            self.status = GameStatus.DRAW_INSUFFICIENT
        else:
            self.status = GameStatus.ACTIVE
    
    def _is_insufficient_material(self):
        """Check if there is insufficient material to checkmate."""
        white_pieces = self.board.get_all_pieces(Color.WHITE)
        black_pieces = self.board.get_all_pieces(Color.BLACK)
        
        # Filter out kings
        white_non_kings = [p for p in white_pieces if p.piece_type != PieceType.KING]
        black_non_kings = [p for p in black_pieces if p.piece_type != PieceType.KING]
        
        total_non_kings = len(white_non_kings) + len(black_non_kings)
        
        # King vs King
        if total_non_kings == 0:
            return True
        
        # King + minor piece vs King
        if total_non_kings == 1:
            piece = white_non_kings[0] if white_non_kings else black_non_kings[0]
            if piece.piece_type in [PieceType.BISHOP, PieceType.KNIGHT]:
                return True
        
        # King + Bishop vs King + Bishop (same color bishops)
        if (len(white_non_kings) == 1 and len(black_non_kings) == 1 and
            white_non_kings[0].piece_type == PieceType.BISHOP and
            black_non_kings[0].piece_type == PieceType.BISHOP):
            # Check if bishops are on same color squares
            w_bishop_pos = white_non_kings[0].position
            b_bishop_pos = black_non_kings[0].position
            w_square_color = (w_bishop_pos[0] + w_bishop_pos[1]) % 2
            b_square_color = (b_bishop_pos[0] + b_bishop_pos[1]) % 2
            if w_square_color == b_square_color:
                return True
        
        return False
    
    def undo_move(self):
        """Undo the last move."""
        if not self.move_history:
            return False
        
        move = self.move_history.pop()
        
        # Handle castling undo
        if move.is_castling:
            self._undo_castling(move)
        # Handle en passant undo
        elif move.is_en_passant:
            self._undo_en_passant(move)
        # Handle promotion undo
        elif move.promotion_piece:
            self._undo_promotion(move)
        # Handle normal move undo
        else:
            self._undo_normal_move(move)
        
        # Restore piece's has_moved state
        move.piece.has_moved = move.piece_had_moved
        
        # Switch back to previous player
        self.switch_player()
        
        # Restore en passant target from previous move if exists
        if self.move_history:
            prev_move = self.move_history[-1]
            if (prev_move.piece.piece_type == PieceType.PAWN and
                abs(prev_move.to_pos[0] - prev_move.from_pos[0]) == 2):
                en_passant_row = (prev_move.from_pos[0] + prev_move.to_pos[0]) // 2
                self.en_passant_target = (en_passant_row, prev_move.to_pos[1])
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None
        
        # Update move counters
        if self.current_player == Color.BLACK:
            self.fullmove_number -= 1
        
        # Recalculate game status
        self._update_game_status()
        
        return True
    
    def _undo_normal_move(self, move):
        """Undo a normal move."""
        self.board.set_piece(move.from_pos, move.piece)
        self.board.set_piece(move.to_pos, move.captured)
        move.piece.position = move.from_pos
        if move.captured:
            move.captured.position = move.to_pos
    
    def _undo_castling(self, move):
        """Undo a castling move."""
        king = move.piece
        row = move.from_pos[0]
        
        # Restore king position
        self.board.set_piece(move.from_pos, king)
        self.board.set_piece(move.to_pos, None)
        king.position = move.from_pos
        
        # Restore rook position
        if move.castling_side == 'kingside':
            rook = self.board.get_piece((row, KINGSIDE_ROOK_DEST))
            self.board.set_piece((row, KINGSIDE_ROOK_COL), rook)
            self.board.set_piece((row, KINGSIDE_ROOK_DEST), None)
            rook.position = (row, KINGSIDE_ROOK_COL)
            rook.has_moved = False
        else:
            rook = self.board.get_piece((row, QUEENSIDE_ROOK_DEST))
            self.board.set_piece((row, QUEENSIDE_ROOK_COL), rook)
            self.board.set_piece((row, QUEENSIDE_ROOK_DEST), None)
            rook.position = (row, QUEENSIDE_ROOK_COL)
            rook.has_moved = False
    
    def _undo_en_passant(self, move):
        """Undo an en passant capture."""
        pawn = move.piece
        captured_pawn_pos = (move.from_pos[0], move.to_pos[1])
        
        self.board.set_piece(move.from_pos, pawn)
        self.board.set_piece(move.to_pos, None)
        self.board.set_piece(captured_pawn_pos, move.captured)
        pawn.position = move.from_pos
        if move.captured:
            move.captured.position = captured_pawn_pos
    
    def _undo_promotion(self, move):
        """Undo a pawn promotion."""
        # Create a new pawn to replace the promoted piece
        pawn = Pawn(move.piece.color, move.from_pos)
        pawn.has_moved = move.piece_had_moved
        
        self.board.set_piece(move.from_pos, pawn)
        self.board.set_piece(move.to_pos, move.captured)
        if move.captured:
            move.captured.position = move.to_pos
    
    def get_all_legal_moves(self, color=None):
        """Get all legal moves for a player."""
        if color is None:
            color = self.current_player
        
        all_moves = []
        for piece in self.board.get_all_pieces(color):
            moves = self.get_legal_moves(piece)
            for move in moves:
                all_moves.append((piece.position, move))
        
        return all_moves
    
    def is_game_over(self):
        """Check if the game is over."""
        return self.status in [
            GameStatus.CHECKMATE,
            GameStatus.STALEMATE,
            GameStatus.DRAW_FIFTY_MOVE,
            GameStatus.DRAW_THREEFOLD,
            GameStatus.DRAW_INSUFFICIENT,
            GameStatus.RESIGNED
        ]
    
    def get_winner(self):
        """Get the winner of the game, if any."""
        if self.status == GameStatus.CHECKMATE:
            # The player who just moved wins
            return Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        return None