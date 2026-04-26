# File name : main.py
# Content: A Gomoku game implementation in Python without any imported libraries.
from AI.base import BaseAI
from AI.Heuristic_ai_depth import HeuristicAIDepth
from human import Human
from board import Board

def main():
    print("Welcome to Gomoku!")
    # Initialize the board size, default is 15x15
    size = 15
    while True:
        print(f"Enter board size (default {size}):")
        input_size = input()
        if input_size == "":
            break
        elif input_size.isdigit() and 5 <= int(input_size) :
            size = int(input_size)
            break
        else:
            print("Invalid input. Please enter a number between 5 and 25, or press Enter to use the default size.")
    board = Board(size)

    # Create players based on user choice: Human vs AI or Human vs Human
    print("Do you want to play against the AI? (y/n):")
    cin = input()
    if cin == "test":
        print("Choose an AI difficulty level(from 1 to 4) for player 1:")
        while True:
            ai_choice = input("1: Easy, 2: Medium, 3: Hard, 4: Expert (default 3): ")
            if ai_choice in ['1', '2', '3', '4']:
                break
            print("Invalid choice, please enter a number between 1 and 4.")
        print("Choose an AI difficulty level(from 1 to 4) for player 2:")
        while True:
            ai_choice2 = input("1: Easy, 2: Medium, 3: Hard, 4: Expert (default 3): ")
            if ai_choice2 in ['1', '2', '3', '4']:
                break
            print("Invalid choice, please enter a number between 1 and 4.")
        player1 = HeuristicAIDepth(board, 1, depth=int(ai_choice))
        player2 = HeuristicAIDepth(board, 2, depth=int(ai_choice2))

    else:
        play_ai = cin.lower() == 'y'

        if play_ai:
            print("Do you want to be Player 1 or Player 2? (Enter 1 or 2):")
            human_player = 1 if int(input()) == 1 else 2
            ai_player = 2 if human_player == 1 else 1
            print("Choose an AI difficulty level(from 1 to 4):")
            while True:
                ai_choice = input("1: Easy, 2: Medium, 3: Hard, 4: Expert (default 3): ") or "3"
                if ai_choice in ['1', '2', '3', '4']:
                    break
                print("Invalid choice, please enter a number between 1 and 4.")
            if ai_choice not in ['1', '2', '3', '4']:
                print("Invalid choice, defaulting to level 3.")
                ai_choice = '3'
            if ai_player == 1:
                player1 = HeuristicAIDepth(board, ai_player, depth=int(ai_choice))
                player2 = Human(board, human_player)
            else:
                player1 = Human(board, human_player)
                player2 = HeuristicAIDepth(board, ai_player, depth=int(ai_choice))
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