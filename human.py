import re
from typing import Optional, Tuple
from AI.base import BaseAI

class Human(BaseAI):
    """
    Human player class for Gomoku.
    This class allows a human player to input their moves via the console. It validates the input to ensure that it is in the correct format and that the move is legal on the board.
    The human player can enter their move as "row,col" or "row col" (e.g., "3,4" or "3 4"), and the class will parse this input and return the corresponding coordinates for the game logic to process.
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
        The method prompts the user to enter their move in the format "row,col" or "row col".
        It validates the input format, integer conversion, board bounds, and whether the target cell is empty.
        If the input is valid, it returns a tuple (row, col) representing the move. If the input is invalid, it prompts the user to try again until a valid move is entered.
        :return: A tuple (row, col) representing the human player's chosen move, or None if no valid move is entered.
        """
        board_size = self.board.size
        while True:
            move_input = input("请输入坐标（行,列 或 行 列）：").strip()
            parts = [part for part in re.split(r"[,\s，]+", move_input) if part]
            if len(parts) != 2:
                print("请输入两个整数，例如 3 4")
                continue

            row_str, col_str = parts
            try:
                row = int(row_str) - 1  # Convert to 0-based index
                col = int(col_str) - 1  # Convert to 0-based index
            except ValueError:
                print("行和列都必须是整数。")
                continue

            if not (0 <= row < board_size and 0 <= col < board_size):
                print(f"坐标越界，请输入 1 到 {board_size} 之间的整数。")
                continue

            if not self.board.is_legal_move((row, col)):
                print("该位置已被占用，请重新选择。")
                continue

            return (row, col)
