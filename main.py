# File name : main.py
# Content: A Gomoku game implementation in Python without any imported libraries.
from AI.base import BaseAI
from AI.Heuristic_ai import HeuristicAI 
from human import Human
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
        print("  " + " ".join(f"{i+1:2}" for i in range(self.size)))  # Print column numbers
        for i, row in enumerate(self.board):
            print(f"{i+1:2} " + '  '.join(str(cell) for cell in row))




# def main():
#     print("Welcome to Gomoku!")
#     print("Choose the size of the board (default is 15):")
#     try:
#         size = int(input())
#         board = Board(size)
#     except ValueError:
#         board = Board()
#     current_player = 1
#     print("Do you want to play against the AI? (y/n):")
#     print("Enter 'y' for yes or 'n' for no:")
#     play_ai = input().lower() == 'y'
#     ai_player = None
#     if play_ai:
#         print("Do you want to be Player 1 or Player 2? (Enter 1 or 2):")
#         ai_player = 2 if int(input()) == 1 else 1

#     # The main loop of the game will continue until a player wins or the board is full. In each iteration, 
#     # we will print the current state of the board, prompt the current player for their move, and check for a win condition after each move. 
#     # If the player is an AI, we will call the make_move function to let the AI make its move. 
#     if play_ai :
#         while True:
#             board.print_board()
#             print("-" * (board.size * 2 - 1))
#             if current_player == ai_player:
#                 print(f"AI Player {current_player}'s turn.")
#                 ai_player_instance = normalAIplayer(board, current_player)
#                 move = ai_player_instance.make_move()
#                 row, col = move[0], move[1]  # Get the last move made by the AI for win checking
#                 print(f"AI Player {current_player} placed a piece at ({row + 1}, {col + 1}).")
#             else:
#                 print(f"Player {current_player}'s turn. Enter row and column (1-{board.size}):")
#                 try:
#                     row, col = map(int, input().split())
#                     if not board.place(current_player, [row - 1, col - 1]):
#                         print("Invalid move. Try again.")
#                         continue
#                 except ValueError:
#                     print("Invalid input. Please enter two integers separated by a space.")
#                     continue
#                 print(f"Player {current_player} placed a piece at ({row}, {col}).")
#                 row -= 1  # Adjust for zero-based indexing
#                 col -= 1  # Adjust for zero-based indexing
#             if board.check_win(current_player, [row , col]):
#                 board.print_board()
#                 print(f"Player {current_player} wins!")
#                 break
#             current_player = 2 if current_player == 1 else 1


#     if not play_ai:
#         while True:
#             board.print_board()
#             print("-" * (board.size * 2 - 1))
#             print(f"Player {current_player}'s turn. Enter row and column (1-{board.size}):")
#             # The input is expected to be two integers separated by a space, representing the row and column where the player wants to place their piece.
#             try:
#                 row, col = map(int, input().split())
#                 if board.place(current_player, [row - 1, col - 1]):
#                     if board.check_win(current_player, [row - 1, col - 1]):
#                         board.print_board()
#                         print(f"Player {current_player} wins!")
#                         break
#                     current_player = 2 if current_player == 1 else 1
#                 else:
#                     print("Invalid move. Try again.")
#             except ValueError:
#                 print("Invalid input. Please enter two integers separated by a space.")
#             # The game continues until a player wins or the board is full.
#             print(f"Player {current_player} placed a piece at ({row}, {col}).")
#             if all(cell != 0 for row in board.board for cell in row):
#                 board.print_board()
#                 print("It's a draw!")
#                 break

# if __name__ == "__main__":
#     main()





def main():
    print("Welcome to Gomoku!")
    # Initialize the board size, default is 15x15
    size = 15
    try:
        size = int(input("Choose board size (default 15): ") or "15")
    except ValueError:
        pass
    board = Board(size)

    # Create players based on user choice: Human vs AI or Human vs Human
    print("Do you want to play against the AI? (y/n):")
    play_ai = input().lower() == 'y'

    if play_ai:
        print("Do you want to be Player 1 or Player 2? (Enter 1 or 2):")
        human_player = 1 if int(input()) == 1 else 2
        ai_player = 2 if human_player == 1 else 1
        print("Choos a AI difficulty level: 1 for Heuristic AI, 2 for Random AI (not finished yet):")
        ai_choice = input("Enter 1 or 2: ")
        if ai_choice == '1':
            if human_player == 1:
                player1 = Human(board, human_player)
                player2 = HeuristicAI(board, ai_player)
            else:
                player1 = HeuristicAI(board, ai_player)
                player2 = Human(board, human_player)
        elif ai_choice == '2':
            print("Random AI is not implemented yet. Defaulting to Heuristic AI.")
            if human_player == 1:
                player1 = Human(board, human_player)
                player2 = HeuristicAI(board, ai_player)
            else:
                player1 = HeuristicAI(board, ai_player)
                player2 = Human(board, human_player)
    else:
        player1 = Human(board, 1)
        player2 = Human(board, 2)

    # The main loop of the game.
    current_player = player1   
    while True:
        board.print_board()
        print("-" * (board.size * 2 - 1))
        print(f"Player {current_player.player}'s turn.")

        move = current_player.get_move()
        if move is None:
            print(f"Player {current_player.player} has no valid moves. Game ends in a draw.")
            break

        row, col = move

        # Perform the move and check if it's valid. The get_move method should ensure that the move is valid, but we check again just in case.
        if not board.place(current_player.player, [row, col]):
            print("Invalid move, try again.")
            continue

        print(f"Player {current_player.player} placed a piece at ({row+1}, {col+1}).")
        # Check for a win condition after the move. If the current player wins, print the board and announce the winner, then break the loop to end the game.
        if board.check_win(current_player.player, [row, col]):
            board.print_board()
            print(f"Player {current_player.player} wins!")
            break

        # Check for a draw condition. If the board is full and no player has won, print the board and announce a draw, then break the loop to end the game.
        if all(cell != 0 for row_cells in board.board for cell in row_cells):
            board.print_board()
            print("It's a draw!")
            break

        # Switch to the other player for the next turn. If the current player is player1, switch to player2, and vice versa.
        current_player = player2 if current_player == player1 else player1

if __name__ == "__main__":
    main()