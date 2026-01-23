# Chess Game

A fully-featured chess game implementation in Python with a graphical user interface.

## Features

### Core Game Logic ✅
- Complete chess rules implementation
- All piece movements (including special moves)
- Castling (kingside and queenside)
- En passant capture
- Pawn promotion with piece selection dialog
- Check and checkmate detection
- Stalemate detection
- Draw conditions:
  - Insufficient material
  - 50-move rule
  - Threefold repetition (detection implemented, history tracking pending)

### User Interface ✅
- Clean, intuitive graphical interface using Pygame
- Click-based piece selection and movement
- Legal move highlighting
- Visual indicators for:
  - Selected piece
  - Legal moves (dots on valid squares)
  - Last move played
  - Check status
  - Current player turn
- Coordinate labels (files and ranks)

### Game Modes ✅
- Player vs Player (local)
- Player vs AI (with placeholder random moves)
- Main menu for game mode selection

### Additional Features ✅
- Move undo functionality (press U)
- Game reset (press R)
- Board flip option (press F)
- Toggle legal move display (press L)
- Game over dialogs with play again option

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt