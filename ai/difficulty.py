from enum import Enum
from core.init import Difficulty

class DifficultyConfig:
    """Configuration for different AI difficulty levels."""
    
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self._configure()
        
    def _configure(self):
        """Set parameters based on difficulty level."""
        if self.difficulty == Difficulty.BEGINNER:
            self.depth = 1
            self.randomness = 0.3
            self.use_piece_tables = False
            self.use_king_safety = False
            self.use_pawn_structure = False
            
        elif self.difficulty == Difficulty.INTERMEDIATE:
            self.depth = 3
            self.randomness = 0.0
            self.use_piece_tables = True
            self.use_king_safety = False
            self.use_pawn_structure = False
            
        elif self.difficulty == Difficulty.ADVANCED:
            self.depth = 5
            self.randomness = 0.0
            self.use_piece_tables = True
            self.use_king_safety = True
            self.use_pawn_structure = True