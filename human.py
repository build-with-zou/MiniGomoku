from typing import Optional, Tuple
from AI.base import BaseAI

class Human(BaseAI):
    """
    Human player class for Gomoku.
    This class allows a human player to input their moves via the console. It validates the input to ensure that it is in the correct format and that the move is legal on the board.
    The human player can enter their move as "row,col" (e.g., "3,4"), and the class will parse this input and return the corresponding coordinates for the game logic to process.
    """
    def __init__(self, board, player: int):
        """
        Initialize the human player.
        :param board: Board object (instance of the Board class)
        :param player: Player number that the human represents (1 or 2)
        """
        super().__init__(board, player)

    def get_move(self) -> Optional[Tuple[int, int]]:
        """
        Get a move from the human player via console input.
        The method prompts the user to enter their move in the format "row,col". It validates the input and ensures that it corresponds to a valid move on the board.
        If the input is valid, it returns a tuple (row, col) representing the move. If the input is invalid, it prompts the user to try again until a valid move is entered.
        :return: A tuple (row, col) representing the human player's chosen move, or None if no valid move is entered.
        """
        while True:
            try:
                move_input = input("Enter your move (row,col): ")
                row_str, col_str = move_input.split(' ')
                row = int(row_str.strip()) - 1  # Convert to 0-based index
                col = int(col_str.strip()) - 1  # Convert to 0-based index
                return (row, col)
            except ValueError:
                print("Invalid input. Please enter two integers separated by a space (e.g., '3 4').")
    