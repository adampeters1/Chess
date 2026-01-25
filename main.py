"""
Chess Game - Main Entry Point

A fully-featured chess game with GUI interface, supporting player vs player
and player vs AI modes.
"""

import pygame
import sys
import os
from ai.init import ChessAI
from core.init import Game, GameMode, Difficulty
from gui.interface import ChessInterface

def show_main_menu():
    """Display the main menu and return selected game mode and difficulty."""
    pygame.init()
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Chess Game - Main Menu")
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    BLUE = (0, 100, 200)
    
    # Fonts
    title_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    
    # Menu state
    selected_mode = None
    selected_difficulty = Difficulty.INTERMEDIATE
    
    # Button definitions
    buttons = {
        'pvp': pygame.Rect(100, 150, 200, 50),
        'pva': pygame.Rect(100, 220, 200, 50),
        'beginner': pygame.Rect(50, 320, 100, 40),
        'intermediate': pygame.Rect(150, 320, 100, 40),
        'advanced': pygame.Rect(250, 320, 100, 40),
        'start': pygame.Rect(100, 420, 200, 50)
    }
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Check game mode buttons
                if buttons['pvp'].collidepoint(mouse_pos):
                    selected_mode = GameMode.PLAYER_VS_PLAYER
                elif buttons['pva'].collidepoint(mouse_pos):
                    selected_mode = GameMode.PLAYER_VS_AI
                
                # Check difficulty buttons (only if PvA selected)
                if selected_mode == GameMode.PLAYER_VS_AI:
                    if buttons['beginner'].collidepoint(mouse_pos):
                        selected_difficulty = Difficulty.BEGINNER
                    elif buttons['intermediate'].collidepoint(mouse_pos):
                        selected_difficulty = Difficulty.INTERMEDIATE
                    elif buttons['advanced'].collidepoint(mouse_pos):
                        selected_difficulty = Difficulty.ADVANCED
                
                # Check start button
                if buttons['start'].collidepoint(mouse_pos) and selected_mode:
                    return selected_mode, selected_difficulty
        
        # Clear screen
        screen.fill(WHITE)
        
        # Draw title
        title_text = title_font.render("Chess Game", True, BLACK)
        title_rect = title_text.get_rect(center=(200, 50))
        screen.blit(title_text, title_rect)
        
        # Draw game mode selection
        mode_text = button_font.render("Select Game Mode:", True, BLACK)
        mode_rect = mode_text.get_rect(center=(200, 110))
        screen.blit(mode_text, mode_rect)
        
        # Draw PvP button
        pvp_color = BLUE if selected_mode == GameMode.PLAYER_VS_PLAYER else LIGHT_GRAY
        pygame.draw.rect(screen, pvp_color, buttons['pvp'])
        pygame.draw.rect(screen, BLACK, buttons['pvp'], 2)
        pvp_text = button_font.render("Player vs Player", True, WHITE if selected_mode == GameMode.PLAYER_VS_PLAYER else BLACK)
        pvp_text_rect = pvp_text.get_rect(center=buttons['pvp'].center)
        screen.blit(pvp_text, pvp_text_rect)
        
        # Draw PvA button
        pva_color = BLUE if selected_mode == GameMode.PLAYER_VS_AI else LIGHT_GRAY
        pygame.draw.rect(screen, pva_color, buttons['pva'])
        pygame.draw.rect(screen, BLACK, buttons['pva'], 2)
        pva_text = button_font.render("Player vs AI", True, WHITE if selected_mode == GameMode.PLAYER_VS_AI else BLACK)
        pva_text_rect = pva_text.get_rect(center=buttons['pva'].center)
        screen.blit(pva_text, pva_text_rect)
        
        # Draw difficulty selection (only if PvA selected)
        if selected_mode == GameMode.PLAYER_VS_AI:
            diff_text = small_font.render("Select Difficulty:", True, BLACK)
            diff_rect = diff_text.get_rect(center=(200, 290))
            screen.blit(diff_text, diff_rect)
            
            # Draw difficulty buttons with color coding: green (easy), blue (medium), red (hard)
            difficulty_colors = {
                Difficulty.BEGINNER: (0, 200, 0),       # Green
                Difficulty.INTERMEDIATE: (0, 100, 200), # Blue
                Difficulty.ADVANCED: (200, 0, 0)        # Red
            }
            for diff, button_key in [(Difficulty.BEGINNER, 'beginner'), 
                                     (Difficulty.INTERMEDIATE, 'intermediate'), 
                                     (Difficulty.ADVANCED, 'advanced')]:
                button = buttons[button_key]
                color = difficulty_colors[diff]
                pygame.draw.rect(screen, color, button)
                pygame.draw.rect(screen, BLACK, button, 2)
                
                text = small_font.render(diff.name.capitalize(), True, WHITE if selected_difficulty == diff else BLACK)
                text_rect = text.get_rect(center=button.center)
                screen.blit(text, text_rect)
        
        # Draw start button
        start_color = BLUE if selected_mode else GRAY
        pygame.draw.rect(screen, start_color, buttons['start'])
        pygame.draw.rect(screen, BLACK, buttons['start'], 2)
        start_text = button_font.render("Start Game", True, WHITE)
        start_text_rect = start_text.get_rect(center=buttons['start'].center)
        screen.blit(start_text, start_text_rect)
        
        # Draw instructions
        instructions = [
            "Use mouse to select and move pieces",
            "Press U to undo, R to reset",
            "Press F to flip board, L to toggle legal moves"
        ]
        y = 530
        for instruction in instructions:
            inst_text = small_font.render(instruction, True, BLACK)
            inst_rect = inst_text.get_rect(center=(200, y))
            screen.blit(inst_text, inst_rect)
            y += 25
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

def main():
    """Main entry point for the chess application."""
    # Show main menu
    game_mode, difficulty = show_main_menu()
    
    # Create game instance
    game = Game(mode=game_mode, difficulty=difficulty)
    
    # Create and run interface
    interface = ChessInterface(game)
    interface.run()

if __name__ == "__main__":
    # Ensure we're running from the correct directory
    if not os.path.exists('core') or not os.path.exists('gui'):
        print("Error: Please run the game from the project root directory.")
        print("Usage: python main.py")
        sys.exit(1)
    
    main()