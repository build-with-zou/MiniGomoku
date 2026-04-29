# File name:gui.py
# Content : Graphical User Interface for Gomoku game

# gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from board import Board
from AI.Heuristic_ai_depth import HeuristicAIDepth

class GomokuGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("五子棋 - Gomoku")
        self.window.resizable(False, False)
        
        # The initial settings
        self.size = 15          # Default board size
        self.cell_size = 40     # Pixels per cell
        self.ai_player = None   # AI object
        self.human_player = 1   # Human player number
        self.ai_side = None     # AI side
        self.depth = 2          # AI search depth
        self.board = None       # Board instance
        self.current_player = 1
        self.game_over = False
        
        # Start game setup
        self.setup_game()
        
        # If the user cancels the setup, exit directly
        if self.board is None:
            self.window.destroy()
            return
        
        self.create_widgets()
        self.draw_board()
        
        # If AI goes first, let it make the first move
        if self.current_player == self.ai_side:
            self.window.after(300, self.ai_move)
        
        self.window.mainloop()
    
    def setup_game(self):
        """Set up the game by asking user preferences"""
        # Choose board size
        size_str = simpledialog.askstring("Board Size", "Enter board size (default 15):", initialvalue="15")
        if size_str is None:
            return
        try:
            self.size = int(size_str)
        except ValueError:
            self.size = 15
        
        # Whether to play against AI
        play_ai = messagebox.askyesno("Game Mode", "Do you want to play against AI?")
        if play_ai:
            # Choose side
            side = simpledialog.askinteger("Choose Side", "Do you want to play as Black (1) or White (2)?", minvalue=1, maxvalue=2)
            if side is None:
                return
            self.human_player = side
            self.ai_side = 2 if side == 1 else 1
            
            # Choose AI difficulty
            depth = simpledialog.askinteger("AI Difficulty", "Enter search depth (1-4):", minvalue=1, maxvalue=4, initialvalue=2)
            if depth is None:
                return
            self.depth = depth
            
            # Create Board and AI objects
            self.board = Board(self.size)
            self.ai_player = HeuristicAIDepth(self.board, player=self.ai_side, depth=self.depth)
        else:
            # Two-player mode
            self.board = Board(self.size)
            self.ai_side = None
        
        self.current_player = 1  # Black goes first
    
    def create_widgets(self):
        """Create canvas and status bar"""
        canvas_width = self.cell_size * (self.size + 1)
        canvas_height = self.cell_size * (self.size + 1)
        
        self.canvas = tk.Canvas(self.window, width=canvas_width, height=canvas_height, bg="#DEB887")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click) # Bind left mouse click to the on_click method
        
        # Status bar
        self.status_var = tk.StringVar()
        self.update_status()
        status_label = tk.Label(self.window, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Buttons: Restart, Quit
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)
        restart_btn = tk.Button(button_frame, text="Restart", command=self.restart)
        restart_btn.pack(side=tk.LEFT, padx=10)
        quit_btn = tk.Button(button_frame, text="Quit", command=self.window.quit)
        quit_btn.pack(side=tk.LEFT, padx=10)
    
    def draw_board(self):
        """Draw the board grid and pieces"""
        self.canvas.delete("all")
        s = self.cell_size
        n = self.size
        # grid lines
        for i in range(n):
            self.canvas.create_line(s, s + i * s, s * n, s + i * s)
            self.canvas.create_line(s + i * s, s, s + i * s, s * n)
        
        # star points (dynamic)
        star_points = set()
        center = n // 2
        star_points.add((center, center))
        if n >= 9:
            offset = 3
            if offset < center:
                star_points.update([
                    (offset, offset),
                    (offset, n - 1 - offset),
                    (n - 1 - offset, offset),
                    (n - 1 - offset, n - 1 - offset)
                ])
        for r, c in star_points:
            x = s * (c + 1)
            y = s * (r + 1)
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")
        
        # Redraw all pieces
        for r in range(n):
            for c in range(n):
                piece = self.board.board[r][c]
                if piece != 0:
                    self.draw_piece(r, c, piece)
    
    def draw_piece(self, row, col, player):
        """Draw a piece at the specified position"""
        x = self.cell_size * (col + 1)
        y = self.cell_size * (row + 1)
        r = self.cell_size // 2 - 2
        color = "black" if player == 1 else "white"
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=1)
    
    def on_click(self, event):
        """Handle mouse click event for placing a piece"""
        if self.game_over:
            return
        # If AI is thinking, do not respond to clicks
        if self.ai_side and self.current_player == self.ai_side:
            return
        
        # Calculate row and column from click coordinates
        col = round((event.x - self.cell_size) / self.cell_size)
        row = round((event.y - self.cell_size) / self.cell_size)
        if 0 <= row < self.size and 0 <= col < self.size:
            if self.board.place(self.current_player, [row, col]):
                self.draw_piece(row, col, self.current_player)
                if self.check_game_over(row, col):
                    return
                self.switch_player()
                # If it's AI's turn, make the AI move
                if self.ai_side and self.current_player == self.ai_side:
                    self.window.after(200, self.ai_move)
    
    def ai_move(self):
        """AI move logic"""
        if self.game_over:
            return
        move = self.ai_player.get_move()
        if move is not None:
            r, c = move
            success = self.board.place(self.current_player, [r, c])
            if success:
                self.draw_piece(r, c, self.current_player)
                if not self.check_game_over(r, c):
                    self.switch_player()
    
    def check_game_over(self, row, col):
        """Check if the game is over after the last move"""
        if self.board.check_win(self.current_player, [row, col]):
            self.game_over = True
            winner = "Black (Player 1)" if self.current_player == 1 else "White (Player 2)"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.update_status()
            return True
        if self.board.is_full():
            self.game_over = True
            messagebox.showinfo("Game Over", "平局!")
            self.update_status()
            return True
        return False
    
    def switch_player(self):
        """Switch the current player"""
        self.current_player = 3 - self.current_player
        self.update_status()
    
    def update_status(self):
        """Update the status bar text"""
        if self.game_over:
            self.status_var.set("Game Over")
        else:
            player_text = "Black" if self.current_player == 1 else "White"
            if self.ai_side and self.current_player == self.ai_side:
                player_text += " (AI Thinking...)"
            self.status_var.set(f"Current: {player_text}")
    
    def restart(self):
        """Restart the game"""
        self.board = Board(self.size)
        if self.ai_side:
            self.ai_player = HeuristicAIDepth(self.board, player=self.ai_side, depth=self.depth)
        self.current_player = 1
        self.game_over = False
        self.draw_board()
        self.update_status()
        # If AI goes first, make the first move automatically
        if self.ai_side and self.current_player == self.ai_side:
            self.window.after(300, self.ai_move)

if __name__ == "__main__":
    GomokuGUI()