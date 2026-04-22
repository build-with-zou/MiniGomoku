# File name : main.py
# Content: A Gomoku game implementation in Python without any imported libraries.

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
    # Print the current state of the board
    def print_board(self):
        for row in self.board:
            print(' '.join(str(cell) for cell in row))


def main():
    print("Welcome to Gomoku!")
    print("Choose the size of the board (default is 15):")
    try:
        size = int(input())
        board = Board(size)
    except ValueError:
        board = Board()
    current_player = 1
    
    while True:
        board.print_board()
        print("-" * (board.size * 2 - 1))
        print(f"Player {current_player}'s turn. Enter row and column (1-{board.size}):")
        # The input is expected to be two integers separated by a space, representing the row and column where the player wants to place their piece.
        try:
            row, col = map(int, input().split())
            if board.place(current_player, [row - 1, col - 1]):
                if board.check_win(current_player, [row - 1, col - 1]):
                    board.print_board()
                    print(f"Player {current_player} wins!")
                    break
                current_player = 2 if current_player == 1 else 1
            else:
                print("Invalid move. Try again.")
        except ValueError:
            print("Invalid input. Please enter two integers separated by a space.")
        # The game continues until a player wins or the board is full.
        if all(cell != 0 for row in board.board for cell in row):
            board.print_board()
            print("It's a draw!")
            break

if __name__ == "__main__":
    main()