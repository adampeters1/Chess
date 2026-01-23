from core.init import PieceType, Color, GameStatus

class PositionEvaluator:
    """Evaluates chess positions based on various factors."""
    
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    # Piece-square tables for positional bonuses (from white's perspective)
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]
    
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]
    
    KING_MIDGAME_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
    
    def __init__(self, ai_color):
        self.ai_color = ai_color
        
    def evaluate(self, game, config):
        """Evaluate the position from the AI's perspective."""
        if game.status == GameStatus.CHECKMATE:
            return -100000 if game.current_player == self.ai_color else 100000
        
        if game.is_game_over():
            return 0
            
        score = 0
        
        # Material evaluation
        score += self._evaluate_material(game.board)
        
        # Positional evaluation
        if config.use_piece_tables:
            score += self._evaluate_position(game.board)
        
        # King safety
        if config.use_king_safety:
            score += self._evaluate_king_safety(game.board)
        
        # Pawn structure
        if config.use_pawn_structure:
            score += self._evaluate_pawn_structure(game.board)
            
        return score
    
    def _evaluate_material(self, board):
        """Evaluate material balance."""
        score = 0
        for piece in board.get_all_pieces():
            value = self.PIECE_VALUES[piece.piece_type]
            if piece.color == self.ai_color:
                score += value
            else:
                score -= value
        return score
    
    def _evaluate_position(self, board):
        """Evaluate piece positioning."""
        score = 0
        for piece in board.get_all_pieces():
            row, col = piece.position
            
            # Get appropriate table
            if piece.piece_type == PieceType.PAWN:
                table = self.PAWN_TABLE
            elif piece.piece_type == PieceType.KNIGHT:
                table = self.KNIGHT_TABLE
            elif piece.piece_type == PieceType.KING:
                table = self.KING_MIDGAME_TABLE
            else:
                continue
                
            # Apply table value
            if piece.color == Color.WHITE:
                value = table[row][col]
            else:
                value = table[7-row][col]
                
            if piece.color == self.ai_color:
                score += value
            else:
                score -= value
                
        return score
    
    def _evaluate_king_safety(self, board):
        """Basic king safety evaluation."""
        score = 0
        
        for color in [Color.WHITE, Color.BLACK]:
            king = board.find_king(color)
            if not king:
                continue
                
            # Penalty for exposed king (not castled)
            if not king.has_moved:
                safety_bonus = 50
            else:
                safety_bonus = -30
                
            if color == self.ai_color:
                score += safety_bonus
            else:
                score -= safety_bonus
                
        return score
    
    def _evaluate_pawn_structure(self, board):
        """Basic pawn structure evaluation."""
        score = 0
        
        for color in [Color.WHITE, Color.BLACK]:
            pawns = [p for p in board.get_all_pieces(color) if p.piece_type == PieceType.PAWN]
            
            # Penalty for doubled pawns
            files = {}
            for pawn in pawns:
                _, col = pawn.position
                files[col] = files.get(col, 0) + 1
                
            doubled_penalty = sum(count - 1 for count in files.values()) * -10
            
            if color == self.ai_color:
                score += doubled_penalty
            else:
                score -= doubled_penalty
                
        return score