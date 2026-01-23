import random
from copy import deepcopy
from ai.evaluation import PositionEvaluator
from ai.difficulty import DifficultyConfig
from core.init import Color

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
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Order moves for better pruning (captures first)
        ordered_moves = self._order_moves(game, legal_moves)
        
        for from_pos, to_pos in ordered_moves:
            test_game = self._copy_game_state(game)
            test_game.make_move(from_pos, to_pos)
            
            value = self._minimax(test_game, self.config.depth - 1, alpha, beta, False)
            
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
            
            for from_pos, to_pos in moves:
                test_game = self._copy_game_state(game)
                test_game.make_move(from_pos, to_pos)
                eval_score = self._minimax(test_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
                    
            return max_eval
        else:
            min_eval = float('inf')
            moves = game.get_all_legal_moves(self.opponent_color)
            
            for from_pos, to_pos in moves:
                test_game = self._copy_game_state(game)
                test_game.make_move(from_pos, to_pos)
                eval_score = self._minimax(test_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            return min_eval
    
    def _order_moves(self, game, moves):
        """Order moves to improve alpha-beta pruning efficiency."""
        scored_moves = []
        
        for from_pos, to_pos in moves:
            score = 0
            # Prioritize captures
            if game.board.get_piece(to_pos):
                score += 10
            # Prioritize center moves
            if to_pos in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                score += 5
                
            scored_moves.append((score, from_pos, to_pos))
        
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [(move[1], move[2]) for move in scored_moves]
    
    def _copy_game_state(self, game):
        """Create a deep copy of the game state."""
        new_game = deepcopy(game)
        return new_game