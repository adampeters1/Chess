import pygame
import threading
import time
from pygame.locals import *
from core.init import Game, GameMode, Difficulty, Color, GameStatus, PieceType
from gui.renderer import BoardRenderer, GameStatusRenderer
from ai.init import ChessAI

class ChessInterface:
    """
    Main interface handler for chess game user interactions.
    
    Methods:
        __init__(game: Game, screen_size: tuple = (900, 700)) -> None
        run() -> None: Main game loop
        handle_mouse_click(pos: tuple) -> None: Process mouse clicks on board
        handle_mouse_motion(pos: tuple) -> None: Handle mouse hover effects
        handle_keyboard(event: pygame.event.Event) -> None: Process keyboard input
        update_display() -> None: Refresh the entire display
        show_promotion_dialog(position: tuple) -> PieceType: Display pawn promotion choices
        show_game_over_dialog() -> bool: Display game over screen, return True to play again
    """
    
    def __init__(self, game, screen_size=(900, 700)):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Chess Game")
        
        self.game = game
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Rendering components
        self.board_renderer = BoardRenderer(self.screen, board_size=600)
        self.status_renderer = GameStatusRenderer(self.screen, (680, 50))
        
        # Game state
        self.selected_square = None
        self.legal_moves = []
        self.hover_square = None
        self.last_move = None
        
        # UI state
        self.show_legal_moves = True
        self.flip_board = False  # Option to flip board perspective
        self.promotion_piece = None
        
        # Colors
        self.bg_color = (210, 210, 210)
        
        # AI threading state
        self.ai_thinking = False
        self.ai_move_result = None
        self.ai_thinking_start_time = None
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_mouse_click(event.pos)
                    elif event.button == 3:  # Right click
                        self.selected_square = None
                        self.legal_moves = []
                elif event.type == MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == KEYDOWN:
                    self.handle_keyboard(event)
            
            # Update display
            self.update_display()
            
            # Control frame rate
            self.clock.tick(60)
            
            # Handle AI move if it's AI's turn
            if (self.game.mode == GameMode.PLAYER_VS_AI and 
                self.game.current_player == Color.BLACK and 
                not self.game.is_game_over()):
                self._handle_ai_move()
            
            # Check if AI has finished computing its move
            if self.ai_move_result is not None:
                self._apply_ai_move()
        
        pygame.quit()
    
    def handle_mouse_click(self, pos):
        """Process mouse clicks on board."""
        clicked_square = self.board_renderer.get_square_from_pos(pos)
        
        if clicked_square is None:
            return
        
        # If we have a piece selected
        if self.selected_square:
            # Try to make a move
            if clicked_square in self.legal_moves:
                # Check if this is a pawn promotion
                piece = self.game.board.get_piece(self.selected_square)
                promotion_piece_type = None
                
                if (piece and piece.piece_type == PieceType.PAWN):
                    if (piece.color == Color.WHITE and clicked_square[0] == 0) or \
                       (piece.color == Color.BLACK and clicked_square[0] == 7):
                        promotion_piece_type = self.show_promotion_dialog(clicked_square)
                
                # Make the move
                if self.game.make_move(self.selected_square, clicked_square, promotion_piece_type):
                    self.last_move = self.game.move_history[-1] if self.game.move_history else None
                    self.selected_square = None
                    self.legal_moves = []
                    
                    # Check for game over
                    if self.game.is_game_over():
                        if self.show_game_over_dialog():
                            self.game.reset()
                            self.last_move = None
            else:
                # Select new piece or deselect
                self._select_square(clicked_square)
        else:
            # Select piece
            self._select_square(clicked_square)
    
    def _select_square(self, square):
        """Select a square and update legal moves."""
        piece = self.game.board.get_piece(square)
        
        if piece and piece.color == self.game.current_player:
            self.selected_square = square
            self.legal_moves = self.game.get_legal_moves(piece)
        else:
            self.selected_square = None
            self.legal_moves = []
    
    def handle_mouse_motion(self, pos):
        """Handle mouse hover effects."""
        self.hover_square = self.board_renderer.get_square_from_pos(pos)
    
    def handle_keyboard(self, event):
        """Process keyboard input."""
        if event.key == K_u:  # Undo
            if self.game.mode == GameMode.PLAYER_VS_PLAYER or \
               (self.game.mode == GameMode.PLAYER_VS_AI and self.game.current_player == Color.WHITE):
                if self.game.undo_move():
                    # In player vs AI, undo two moves (player and AI)
                    if self.game.mode == GameMode.PLAYER_VS_AI and self.game.move_history:
                        self.game.undo_move()
                    self.selected_square = None
                    self.legal_moves = []
                    self.last_move = self.game.move_history[-1] if self.game.move_history else None
        
        elif event.key == K_r:  # Reset
            self.game.reset()
            self.selected_square = None
            self.legal_moves = []
            self.last_move = None
        
        elif event.key == K_f:  # Flip board
            self.flip_board = not self.flip_board
        
        elif event.key == K_l:  # Toggle legal move display
            self.show_legal_moves = not self.show_legal_moves
    
    def update_display(self):
        """Refresh the entire display."""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw board and pieces
        self.board_renderer.draw_board()
        self.board_renderer.draw_coordinates()
        self.board_renderer.draw_pieces(self.game.board)
        
        # Get check square if in check
        check_square = None
        if self.game.status in [GameStatus.CHECK, GameStatus.CHECKMATE]:
            king = self.game.board.find_king(self.game.current_player)
            if king:
                check_square = king.position
        
        # Draw highlights
        if self.show_legal_moves:
            self.board_renderer.draw_highlights(
                self.selected_square, 
                self.legal_moves,
                self.last_move,
                check_square
            )
        
        # Draw game status
        self.status_renderer.draw_turn_indicator(self.game.current_player)
        self.status_renderer.draw_game_status(self.game.status, self.game.get_winner())
        
        # Draw AI thinking timer if applicable
        if self.ai_thinking and self.ai_thinking_start_time is not None:
            self._draw_thinking_timer()
        
        # Draw controls help
        self._draw_controls()
        
        # Update display
        pygame.display.flip()
    
    def _draw_thinking_timer(self):
        """Draw AI thinking timer below turn indicator."""
        elapsed_time = time.time() - self.ai_thinking_start_time
        font = pygame.font.SysFont('Arial', 16)
        timer_text = f"Opponent thinking for {elapsed_time:.1f} seconds"
        text_surface = font.render(timer_text, True, (100, 100, 100))
        x, y = 680, 115
        self.screen.blit(text_surface, (x, y))
    
    def _draw_controls(self):
        """Draw keyboard controls help."""
        font = pygame.font.SysFont('Arial', 14)
        controls = [
            "U - Undo move",
            "R - Reset game",
            "F - Flip board",
            "L - Toggle legal moves"
        ]
        
        x, y = 680, 400
        for control in controls:
            text = font.render(control, True, (60, 60, 60))
            self.screen.blit(text, (x, y))
            y += 20
    
    def show_promotion_dialog(self, position):
        """Display pawn promotion choices."""
        # Create a simple dialog
        dialog_width, dialog_height = 300, 100
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        # Piece choices
        choices = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        choice_rects = []
        
        # Draw dialog
        running = True
        while running:
            # Draw dialog background
            pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), dialog_rect, 2)
            
            # Draw title
            font = pygame.font.SysFont('Arial', 20)
            title = font.render("Choose promotion piece:", True, (0, 0, 0))
            title_rect = title.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 25))
            self.screen.blit(title, title_rect)
            
            # Draw piece options
            button_width = 60
            spacing = 10
            total_width = len(choices) * button_width + (len(choices) - 1) * spacing
            start_x = dialog_rect.centerx - total_width // 2
            
            choice_rects = []
            for i, piece_type in enumerate(choices):
                x = start_x + i * (button_width + spacing)
                y = dialog_rect.centery
                rect = pygame.Rect(x, y, button_width, 40)
                choice_rects.append((rect, piece_type))
                
                # Draw button
                pygame.draw.rect(self.screen, (200, 200, 200), rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                
                # Draw piece symbol
                text = font.render(piece_type.value, True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    return PieceType.QUEEN  # Default
                elif event.type == MOUSEBUTTONDOWN:
                    for rect, piece_type in choice_rects:
                        if rect.collidepoint(event.pos):
                            return piece_type
        
        return PieceType.QUEEN  # Default
    
    def show_game_over_dialog(self):
        """Display game over screen, return True to play again."""
        # Create dialog
        dialog_width, dialog_height = 400, 200
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        # Determine message
        if self.game.status == GameStatus.CHECKMATE:
            winner = self.game.get_winner()
            message = f"{winner.name} wins by checkmate!"
        elif self.game.status == GameStatus.STALEMATE:
            message = "Game drawn by stalemate!"
        elif self.game.status == GameStatus.DRAW_FIFTY_MOVE:
            message = "Game drawn by 50-move rule!"
        elif self.game.status == GameStatus.DRAW_INSUFFICIENT:
            message = "Game drawn - insufficient material!"
        else:
            message = "Game Over"
        
        running = True
        while running:
            # Draw dialog
            pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), dialog_rect, 3)
            
            # Draw message
            font = pygame.font.SysFont('Arial', 24)
            text = font.render(message, True, (0, 0, 0))
            text_rect = text.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 50))
            self.screen.blit(text, text_rect)
            
            # Draw buttons
            button_font = pygame.font.SysFont('Arial', 20)
            
            # Play again button
            play_again_rect = pygame.Rect(dialog_rect.centerx - 160, dialog_rect.bottom - 80, 140, 40)
            pygame.draw.rect(self.screen, (0, 200, 0), play_again_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), play_again_rect, 2)
            play_text = button_font.render("Play Again", True, (255, 255, 255))
            play_text_rect = play_text.get_rect(center=play_again_rect.center)
            self.screen.blit(play_text, play_text_rect)
            
            # Quit button
            quit_rect = pygame.Rect(dialog_rect.centerx + 20, dialog_rect.bottom - 80, 140, 40)
            pygame.draw.rect(self.screen, (200, 0, 0), quit_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), quit_rect, 2)
            quit_text = button_font.render("Quit", True, (255, 255, 255))
            quit_text_rect = quit_text.get_rect(center=quit_rect.center)
            self.screen.blit(quit_text, quit_text_rect)
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    return False
                elif event.type == MOUSEBUTTONDOWN:
                    if play_again_rect.collidepoint(event.pos):
                        return True
                    elif quit_rect.collidepoint(event.pos):
                        self.running = False
                        return False
        
        return False
    
    def _handle_ai_move(self):
        """Handle AI player move using a background thread."""
        # Don't start a new thread if AI is already thinking
        if self.ai_thinking:
            return
        
        # Initialize AI if not already done
        if not hasattr(self, 'ai_player'):
            self.ai_player = ChessAI(Color.BLACK, self.game.difficulty)
        
        # Start AI computation in background thread
        self.ai_thinking = True
        self.ai_thinking_start_time = time.time()
        ai_thread = threading.Thread(target=self._compute_ai_move, daemon=True)
        ai_thread.start()
    
    def _compute_ai_move(self):
        """Compute AI move in background thread."""
        best_move = self.ai_player.get_best_move(self.game)
        self.ai_move_result = best_move
    
    def _apply_ai_move(self):
        """Apply the computed AI move to the game."""
        best_move = self.ai_move_result
        self.ai_move_result = None
        self.ai_thinking = False
        self.ai_thinking_start_time = None
        
        if best_move:
            from_pos, to_pos = best_move
            self.game.make_move(from_pos, to_pos)
            self.last_move = self.game.move_history[-1] if self.game.move_history else None