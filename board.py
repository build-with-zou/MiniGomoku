class Board:
    # Initialize the board with a given size
    def __init__(self, size=15):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    # Place a piece on the board
    def place(self ,player:int ,pos:list ): 
        """
        Use 1 to represent player 1 and 2 to represent player 2;
        Pos is a list of two integers representing the row and column where the piece is to be placed.
        For example, if player 1 wants to place a piece at row 3 and column 4, the pos would be [2, 3].
        """
        # Check if the position is valid and the cell is empty
        if 0 <= pos[0] < self.size and 0 <= pos[1] < self.size and self.board[pos[0]][pos[1]] == 0:
            self.board[pos[0]][pos[1]] = player
            return True
        return False
    
    # Check if a player has won the game
    def check_win(self, player,pos):
        """
        Check if the specified player has won the game by having five pieces in a row.
        We only have to check for a win condition starting from the last placed piece, as that is the only move that could have resulted in a win.

        Return: True if the player has won, False otherwise."""
        # Check horizontal, vertical, and diagonal (both directions) for a win
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Check in the positive direction
            r, c = pos[0] + dr, pos[1] + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Check in the negative direction
            r, c = pos[0] - dr, pos[1] - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False
    
    def is_empty(self):
        """
        Check if the board is empty, which can be used to determine if the AI should place the first piece in the center.
        Return: True if the board is empty, False otherwise.
        """
        for row in self.board:
            for cell in row:
                if cell != 0:
                    return False
        return True
    
    def is_full(self):
        """
        Check if the board is full, which would indicate a draw if no player has won.
        Return: True if the board is full, False otherwise.
        """
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    # Print the current state of the board
    def print_board(self):
        print("  " + " ".join(f"{i+1:2}" for i in range(self.size)))  # Print column numbers
        for i, row in enumerate(self.board):
            print(f"{i+1:2} " + '  '.join(str(cell) for cell in row))
