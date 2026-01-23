import pygame
import os
from core.piece import Color, PieceType
from core.constants import BOARD_SIZE, FILES, RANKS

class BoardRenderer:
    """
    Handles all visual rendering of the chess board and pieces.
    
    Methods:
        __init__(screen: pygame.Surface, board_size: int = 600) -> None
        load_assets() -> None: Load piece images and colors
        draw_board() -> None: Draw the chess board squares
        draw_pieces(board: Board) -> None: Draw all pieces on the board
        draw_highlights(selected_pos: tuple, legal_moves: list) -> None: Highlight selected square and legal moves
        draw_coordinates() -> None: Draw file and rank labels
        get_square_rect(row: int, col: int) -> pygame.Rect: Get rectangle for a board square
    """
    
    def __init__(self, screen, board_size=600):
        self.screen = screen
        self.board_size = board_size
        self.square_size = board_size // BOARD_SIZE
        self.board_offset_x = 50  # Space for rank labels
        self.board_offset_y = 50  # Space for file labels
        
        # Colors
        self.light_square = (240, 217, 181)
        self.dark_square = (181, 136, 99)
        self.highlight_color = (255, 255, 0, 128)  # Yellow with transparency
        self.selected_color = (255, 215, 0)  # Gold
        self.move_dot_color = (0, 0, 0, 64)  # Semi-transparent black
        self.last_move_color = (205, 210, 106)  # Light green
        self.check_color = (255, 0, 0, 128)  # Semi-transparent red
        
        # Piece images dictionary
        self.piece_images = {}
        
        # Font for coordinates
        pygame.font.init()
        self.coord_font = pygame.font.SysFont('Arial', 16)
        
        self.load_assets()
    
    def load_assets(self):
        """Load piece images from assets directory."""
        piece_set_path = os.path.join('assets', 'images', 'pieces')
        
        # Map piece types and colors to file names
        piece_files = {
            (Color.WHITE, PieceType.KING): 'white_king.png',
            (Color.WHITE, PieceType.QUEEN): 'white_queen.png',
            (Color.WHITE, PieceType.ROOK): 'white_rook.png',
            (Color.WHITE, PieceType.BISHOP): 'white_bishop.png',
            (Color.WHITE, PieceType.KNIGHT): 'white_knight.png',
            (Color.WHITE, PieceType.PAWN): 'white_pawn.png',
            (Color.BLACK, PieceType.KING): 'black_king.png',
            (Color.BLACK, PieceType.QUEEN): 'black_queen.png',
            (Color.BLACK, PieceType.ROOK): 'black_rook.png',
            (Color.BLACK, PieceType.BISHOP): 'black_bishop.png',
            (Color.BLACK, PieceType.KNIGHT): 'black_knight.png',
            (Color.BLACK, PieceType.PAWN): 'black_pawn.png',
        }
        
        # Load and scale images
        for (color, piece_type), filename in piece_files.items():
            try:
                image_path = os.path.join(piece_set_path, filename)
                image = pygame.image.load(image_path)
                # Scale to fit square with some padding
                scaled_size = int(self.square_size * 0.85)
                scaled_image = pygame.transform.scale(image, (scaled_size, scaled_size))
                self.piece_images[(color, piece_type)] = scaled_image
            except pygame.error:
                # If images not found, create simple colored rectangles as fallback
                self._create_fallback_piece_image(color, piece_type)
    
    def _create_fallback_piece_image(self, color, piece_type):
        """Create simple fallback images if piece images not found."""
        size = int(self.square_size * 0.8)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a circle for the piece
        piece_color = (255, 255, 255) if color == Color.WHITE else (0, 0, 0)
        pygame.draw.circle(surface, piece_color, (size // 2, size // 2), size // 2)
        
        # Draw piece letter
        font = pygame.font.SysFont('Arial', size // 2, bold=True)
        text_color = (0, 0, 0) if color == Color.WHITE else (255, 255, 255)
        text = font.render(piece_type.value, True, text_color)
        text_rect = text.get_rect(center=(size // 2, size // 2))
        surface.blit(text, text_rect)
        
        self.piece_images[(color, piece_type)] = surface
    
    def draw_board(self):
        """Draw the chess board squares."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                rect = self.get_square_rect(row, col)
                pygame.draw.rect(self.screen, color, rect)
    
    def draw_pieces(self, board):
        """Draw all pieces on the board."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board.get_piece((row, col))
                if piece:
                    image = self.piece_images.get((piece.color, piece.piece_type))
                    if image:
                        rect = self.get_square_rect(row, col)
                        # Center the piece in the square
                        piece_rect = image.get_rect()
                        piece_rect.center = rect.center
                        self.screen.blit(image, piece_rect)
    
    def draw_highlights(self, selected_pos, legal_moves, last_move=None, check_square=None):
        """Highlight selected square, legal moves, last move, and check."""
        # Create a temporary surface for transparency
        highlight_surface = pygame.Surface((self.board_size, self.board_size), pygame.SRCALPHA)
        
        # Highlight last move
        if last_move:
            from_rect = self.get_square_rect(*last_move.from_pos)
            to_rect = self.get_square_rect(*last_move.to_pos)
            
            # Offset rectangles to match board position
            from_rect.x -= self.board_offset_x
            from_rect.y -= self.board_offset_y
            to_rect.x -= self.board_offset_x
            to_rect.y -= self.board_offset_y
            
            pygame.draw.rect(highlight_surface, (*self.last_move_color, 80), from_rect)
            pygame.draw.rect(highlight_surface, (*self.last_move_color, 80), to_rect)
        
        # Highlight check square
        if check_square:
            check_rect = self.get_square_rect(*check_square)
            check_rect.x -= self.board_offset_x
            check_rect.y -= self.board_offset_y
            pygame.draw.rect(highlight_surface, self.check_color, check_rect)
        
        # Highlight selected square
        if selected_pos:
            selected_rect = self.get_square_rect(*selected_pos)
            selected_rect.x -= self.board_offset_x
            selected_rect.y -= self.board_offset_y
            pygame.draw.rect(highlight_surface, self.highlight_color, selected_rect)
            pygame.draw.rect(highlight_surface, self.selected_color, selected_rect, 3)
        
        # Draw legal move indicators
        for move in legal_moves:
            move_rect = self.get_square_rect(*move)
            center_x = move_rect.centerx - self.board_offset_x
            center_y = move_rect.centery - self.board_offset_y
            
            # Check if there's a piece to capture
            if selected_pos:
                from core.board import Board
                # Note: We need access to the board to check for captures
                # For now, draw a dot for all moves
                radius = self.square_size // 8
                pygame.draw.circle(highlight_surface, self.move_dot_color, 
                                 (center_x, center_y), radius)
        
        # Blit the highlight surface
        self.screen.blit(highlight_surface, (self.board_offset_x, self.board_offset_y))
    
    def draw_coordinates(self):
        """Draw file and rank labels around the board."""
        # Draw files (a-h)
        for col, file_label in enumerate(FILES):
            x = self.board_offset_x + col * self.square_size + self.square_size // 2
            y = self.board_offset_y + self.board_size + 10
            
            text = self.coord_font.render(file_label, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # Draw ranks (1-8)
        for row, rank_label in enumerate(RANKS):
            x = self.board_offset_x - 20
            y = self.board_offset_y + row * self.square_size + self.square_size // 2
            
            text = self.coord_font.render(rank_label, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def get_square_rect(self, row, col):
        """Get the rectangle for a board square."""
        x = self.board_offset_x + col * self.square_size
        y = self.board_offset_y + row * self.square_size
        return pygame.Rect(x, y, self.square_size, self.square_size)
    
    def get_square_from_pos(self, pos):
        """Convert screen position to board square coordinates."""
        x, y = pos
        col = (x - self.board_offset_x) // self.square_size
        row = (y - self.board_offset_y) // self.square_size
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None


class GameStatusRenderer:
    """
    Renders game status information including turn indicator and game state messages.
    
    Methods:
        __init__(screen: pygame.Surface, position: tuple) -> None
        draw_turn_indicator(current_player: Color) -> None: Display whose turn it is
        draw_game_status(status: GameStatus, winner: Color = None) -> None: Display check/checkmate/draw
        draw_captured_pieces(captured_white: list, captured_black: list) -> None: Show captured pieces
        draw_move_history(moves: list, display_area: pygame.Rect) -> None: Display move list
    """
    
    def __init__(self, screen, position):
        self.screen = screen
        self.position = position  # (x, y) for top-left of status area
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Colors
        self.text_color = (0, 0, 0)
        self.white_indicator = (255, 255, 255)
        self.black_indicator = (0, 0, 0)
        self.border_color = (128, 128, 128)
    
    def draw_turn_indicator(self, current_player):
        """Display whose turn it is."""
        x, y = self.position
        
        # Draw background
        bg_rect = pygame.Rect(x, y, 200, 60)
        pygame.draw.rect(self.screen, (240, 240, 240), bg_rect)
        pygame.draw.rect(self.screen, self.border_color, bg_rect, 2)
        
        # Draw turn text
        turn_text = self.font.render("Turn:", True, self.text_color)
        self.screen.blit(turn_text, (x + 10, y + 20))
        
        # Draw color indicator circle
        indicator_color = self.white_indicator if current_player == Color.WHITE else self.black_indicator
        pygame.draw.circle(self.screen, indicator_color, (x + 80, y + 30), 15)
        pygame.draw.circle(self.screen, self.border_color, (x + 80, y + 30), 15, 2)
        
        # Draw player name
        player_name = "White" if current_player == Color.WHITE else "Black"
        name_text = self.font.render(player_name, True, self.text_color)
        self.screen.blit(name_text, (x + 110, y + 20))
    
    def draw_game_status(self, status, winner=None):
        """Display check, checkmate, or draw status."""
        x, y = self.position
        y += 80  # Below turn indicator
        
        status_messages = {
            'CHECK': ("Check!", (255, 165, 0)),  # Orange
            'CHECKMATE': ("Checkmate!", (255, 0, 0)),  # Red
            'STALEMATE': ("Stalemate!", (128, 128, 128)),  # Gray
            'DRAW_FIFTY_MOVE': ("Draw - 50 moves", (128, 128, 128)),
            'DRAW_INSUFFICIENT': ("Draw - Insufficient material", (128, 128, 128)),
            'DRAW_THREEFOLD': ("Draw - Repetition", (128, 128, 128))
        }
        
        if status.name in status_messages:
            message, color = status_messages[status.name]
            
            # Draw background
            bg_rect = pygame.Rect(x, y, 200, 50)
            pygame.draw.rect(self.screen, (240, 240, 240), bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 3)
            
            # Draw message
            text = self.font.render(message, True, color)
            text_rect = text.get_rect(center=(x + 100, y + 25))
            self.screen.blit(text, text_rect)
            
            # Draw winner if checkmate
            if status.name == 'CHECKMATE' and winner:
                winner_text = f"{winner.name} wins!"
                winner_surface = self.small_font.render(winner_text, True, self.text_color)
                winner_rect = winner_surface.get_rect(center=(x + 100, y + 80))
                self.screen.blit(winner_surface, winner_rect)
    
    def draw_captured_pieces(self, captured_white, captured_black):
        """Show captured pieces."""
        x, y = self.position
        y += 160  # Below status messages
        
        # Draw section header
        header_text = self.small_font.render("Captured:", True, self.text_color)
        self.screen.blit(header_text, (x, y))
        
        # Draw captured white pieces
        y += 30
        white_text = self.small_font.render("White:", True, self.text_color)
        self.screen.blit(white_text, (x, y))
        
        # TODO: Draw actual piece symbols/images
        
        # Draw captured black pieces
        y += 30
        black_text = self.small_font.render("Black:", True, self.text_color)
        self.screen.blit(black_text, (x, y))
    
    def draw_move_history(self, moves, display_area):
        """Display move list in algebraic notation."""
        if not moves:
            return
        
        # Draw background
        pygame.draw.rect(self.screen, (240, 240, 240), display_area)
        pygame.draw.rect(self.screen, self.border_color, display_area, 2)
        
        # Draw moves
        x, y = display_area.topleft
        x += 10
        y += 10
        
        moves_per_line = 2
        line_height = 25
        
        for i in range(0, len(moves), moves_per_line):
            move_number = i // 2 + 1
            line_text = f"{move_number}."
            
            # Add white move
            if i < len(moves):
                line_text += f" {moves[i]}"
            
            # Add black move
            if i + 1 < len(moves):
                line_text += f" {moves[i + 1]}"
            
            text_surface = self.small_font.render(line_text, True, self.text_color)
            self.screen.blit(text_surface, (x, y))
            y += line_height
            
            # Check if we need to scroll
            if y > display_area.bottom - line_height:
                break