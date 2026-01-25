import random
from copy import deepcopy
from ai.evaluation import PositionEvaluator
from ai.difficulty import DifficultyConfig
from core.init import Color, PieceType
from core.piece import Pawn, Rook, Knight, Bishop, Queen

class ChessAI:
    """Chess AI engine using minimax with alpha-beta pruning."""
    
    def __init__(self, color, difficulty):
        self.color = color
        self.opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        self.evaluator = PositionEvaluator(color)
        self.config = DifficultyConfig(difficulty)
        
    def get_best_move(self, game):
        """Return the best move for the current position."""
        legal_moves = game.get_all_legal_moves(self.color)
        if not legal_moves:
            return None
            
        # Apply randomness for beginner level
        if self.config.randomness > 0 and random.random() < self.config.randomness:
            return random.choice(legal_moves)
        
        # Create a single deep copy to work with, preserving the original game state
        search_game = deepcopy(game)
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Order moves for better pruning (captures first)
        ordered_moves = self._order_moves(search_game, legal_moves)
        
        for from_pos, to_pos in ordered_moves:
            move_info = self._make_move(search_game, from_pos, to_pos)
            
            value = self._minimax(search_game, self.config.depth - 1, alpha, beta, False)
            
            self._unmake_move(search_game, move_info)
            
            if value > best_value:
                best_value = value
                best_move = (from_pos, to_pos)
                
            alpha = max(alpha, value)
            
        return best_move
    
    def _minimax(self, game, depth, alpha, beta, maximizing):
        """Minimax with alpha-beta pruning."""
        if depth == 0 or game.is_game_over():
            return self.evaluator.evaluate(game, self.config)
            
        if maximizing:
            max_eval = float('-inf')
            moves = game.get_all_legal_moves(self.color)
            ordered_moves = self._order_moves(game, moves)
            
            for from_pos, to_pos in ordered_moves:
                move_info = self._make_move(game, from_pos, to_pos)
                eval_score = self._minimax(game, depth - 1, alpha, beta, False)
                self._unmake_move(game, move_info)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
                    
            return max_eval
        else:
            min_eval = float('inf')
            moves = game.get_all_legal_moves(self.opponent_color)
            ordered_moves = self._order_moves(game, moves)
            
            for from_pos, to_pos in ordered_moves:
                move_info = self._make_move(game, from_pos, to_pos)
                eval_score = self._minimax(game, depth - 1, alpha, beta, True)
                self._unmake_move(game, move_info)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            return min_eval
    
    def _make_move(self, game, from_pos, to_pos):
        """Make a move and return info needed to unmake it."""
        piece = game.board.get_piece(from_pos)
        captured = game.board.get_piece(to_pos)
        
        # Store state for unmake
        move_info = {
            'from_pos': from_pos,
            'to_pos': to_pos,
            'piece': piece,
            'captured': captured,
            'piece_had_moved': piece.has_moved,
            'prev_en_passant': game.en_passant_target,
            'prev_player': game.current_player,
            'prev_status': game.status,
            'prev_halfmove': game.halfmove_clock,
            'is_castling': False,
            'is_en_passant': False,
            'is_promotion': False,
            'promoted_piece': None,
            'original_pawn': None
        }
        
        # Detect castling
        if piece.piece_type == PieceType.KING and abs(to_pos[1] - from_pos[1]) == 2:
            move_info['is_castling'] = True
            move_info['castling_side'] = 'kingside' if to_pos[1] > from_pos[1] else 'queenside'
            row = from_pos[0]
            
            if move_info['castling_side'] == 'kingside':
                rook = game.board.get_piece((row, 7))
                move_info['rook'] = rook
                move_info['rook_from'] = (row, 7)
                move_info['rook_to'] = (row, 5)
                move_info['rook_had_moved'] = rook.has_moved
                
                game.board.set_piece((row, 5), rook)
                game.board.set_piece((row, 7), None)
                rook.position = (row, 5)
                rook.has_moved = True
            else:
                rook = game.board.get_piece((row, 0))
                move_info['rook'] = rook
                move_info['rook_from'] = (row, 0)
                move_info['rook_to'] = (row, 3)
                move_info['rook_had_moved'] = rook.has_moved
                
                game.board.set_piece((row, 3), rook)
                game.board.set_piece((row, 0), None)
                rook.position = (row, 3)
                rook.has_moved = True
        
        # Detect en passant
        elif (piece.piece_type == PieceType.PAWN and 
              to_pos == game.en_passant_target and
              game.en_passant_target is not None):
            move_info['is_en_passant'] = True
            captured_pawn_pos = (from_pos[0], to_pos[1])
            move_info['captured'] = game.board.get_piece(captured_pawn_pos)
            move_info['captured_pos'] = captured_pawn_pos
            game.board.set_piece(captured_pawn_pos, None)
        
        # Make the basic move
        game.board.set_piece(to_pos, piece)
        game.board.set_piece(from_pos, None)
        piece.position = to_pos
        piece.has_moved = True
        
        # Handle pawn promotion (default to queen for AI evaluation)
        if piece.piece_type == PieceType.PAWN:
            promotion_row = 0 if piece.color == Color.WHITE else 7
            if to_pos[0] == promotion_row:
                move_info['is_promotion'] = True
                move_info['original_pawn'] = piece
                promoted = Queen(piece.color, to_pos)
                promoted.has_moved = True
                move_info['promoted_piece'] = promoted
                game.board.set_piece(to_pos, promoted)
        
        # Update en passant target
        game.en_passant_target = None
        if piece.piece_type == PieceType.PAWN and abs(to_pos[0] - from_pos[0]) == 2:
            en_passant_row = (from_pos[0] + to_pos[0]) // 2
            game.en_passant_target = (en_passant_row, to_pos[1])
        
        # Switch player
        game.current_player = Color.BLACK if game.current_player == Color.WHITE else Color.WHITE
        
        return move_info
    
    def _unmake_move(self, game, move_info):
        """Unmake a move using stored info."""
        from_pos = move_info['from_pos']
        to_pos = move_info['to_pos']
        piece = move_info['piece']
        
        # Restore player and game state
        game.current_player = move_info['prev_player']
        game.en_passant_target = move_info['prev_en_passant']
        game.status = move_info['prev_status']
        game.halfmove_clock = move_info['prev_halfmove']
        
        # Handle promotion unmake
        if move_info['is_promotion']:
            piece = move_info['original_pawn']
        
        # Restore piece to original position
        game.board.set_piece(from_pos, piece)
        piece.position = from_pos
        piece.has_moved = move_info['piece_had_moved']
        
        # Handle castling unmake
        if move_info['is_castling']:
            game.board.set_piece(to_pos, None)
            rook = move_info['rook']
            game.board.set_piece(move_info['rook_from'], rook)
            game.board.set_piece(move_info['rook_to'], None)
            rook.position = move_info['rook_from']
            rook.has_moved = move_info['rook_had_moved']
        # Handle en passant unmake
        elif move_info['is_en_passant']:
            game.board.set_piece(to_pos, None)
            game.board.set_piece(move_info['captured_pos'], move_info['captured'])
            if move_info['captured']:
                move_info['captured'].position = move_info['captured_pos']
        # Handle normal move unmake
        else:
            game.board.set_piece(to_pos, move_info['captured'])
            if move_info['captured']:
                move_info['captured'].position = to_pos
    
    def _order_moves(self, game, moves):
        """Order moves to improve alpha-beta pruning efficiency.
        
        Prioritizes moves in this order:
        1. Captures (using MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        2. Checks (moves that put opponent in check)
        3. Promotions
        4. Center control moves
        5. Other moves
        """
        scored_moves = []
        enemy_color = Color.BLACK if game.current_player == Color.WHITE else Color.WHITE
        enemy_king = game.board.find_king(enemy_color)
        enemy_king_pos = enemy_king.position if enemy_king else None
        
        for from_pos, to_pos in moves:
            score = 0
            piece = game.board.get_piece(from_pos)
            captured = game.board.get_piece(to_pos)
            
            # Prioritize captures (MVV-LVA)
            if captured:
                victim_value = self._get_piece_value(captured.piece_type)
                attacker_value = self._get_piece_value(piece.piece_type)
                score += 1000 + (10 * victim_value - attacker_value)
            
            # Prioritize checks
            if enemy_king_pos and self._move_gives_check(game, from_pos, to_pos, enemy_king_pos):
                score += 500
            
            # Prioritize pawn promotions
            if piece.piece_type == PieceType.PAWN:
                promotion_row = 0 if piece.color == Color.WHITE else 7
                if to_pos[0] == promotion_row:
                    score += 900
            
            # Prioritize center control
            if to_pos in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                score += 30
            elif to_pos in [(2, 2), (2, 3), (2, 4), (2, 5),
                           (3, 2), (3, 5), (4, 2), (4, 5),
                           (5, 2), (5, 3), (5, 4), (5, 5)]:
                score += 15
            
            # Slight bonus for developing pieces (moving from back rank)
            if piece.piece_type in [PieceType.KNIGHT, PieceType.BISHOP]:
                back_rank = 7 if piece.color == Color.WHITE else 0
                if from_pos[0] == back_rank:
                    score += 10
                
            scored_moves.append((score, from_pos, to_pos))
        
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [(move[1], move[2]) for move in scored_moves]
    
    def _move_gives_check(self, game, from_pos, to_pos, enemy_king_pos):
        """Check if a move would give check to the enemy king."""
        piece = game.board.get_piece(from_pos)
        if not piece:
            return False
        
        # Simulate the piece being at to_pos and check if it attacks the king
        # This is a simplified check - we look at direct attacks only
        piece_type = piece.piece_type
        row_diff = enemy_king_pos[0] - to_pos[0]
        col_diff = enemy_king_pos[1] - to_pos[1]
        
        # Knight check
        if piece_type == PieceType.KNIGHT:
            if (abs(row_diff), abs(col_diff)) in [(1, 2), (2, 1)]:
                return True
        
        # Pawn check
        elif piece_type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            if row_diff == direction and abs(col_diff) == 1:
                return True
        
        # Rook/Queen check (straight lines)
        elif piece_type in [PieceType.ROOK, PieceType.QUEEN]:
            if row_diff == 0 or col_diff == 0:
                if self._is_path_clear(game, to_pos, enemy_king_pos, from_pos):
                    return True
        
        # Bishop/Queen check (diagonals)
        if piece_type in [PieceType.BISHOP, PieceType.QUEEN]:
            if abs(row_diff) == abs(col_diff) and row_diff != 0:
                if self._is_path_clear(game, to_pos, enemy_king_pos, from_pos):
                    return True
        
        return False
    
    def _is_path_clear(self, game, from_pos, to_pos, ignore_pos):
        """Check if path between two positions is clear (ignoring a specific position)."""
        row_diff = to_pos[0] - from_pos[0]
        col_diff = to_pos[1] - from_pos[1]
        
        row_step = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
        
        current_row = from_pos[0] + row_step
        current_col = from_pos[1] + col_step
        
        while (current_row, current_col) != to_pos:
            if (current_row, current_col) != ignore_pos:
                if game.board.get_piece((current_row, current_col)) is not None:
                    return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def _get_piece_value(self, piece_type):
        """Get simple piece value for move ordering."""
        values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 100
        }
        return values.get(piece_type, 0)