from numbers import Integral

import numpy as np

from board import Board


def _validate_move(move, size: int) -> tuple[int, int]:
    if not isinstance(move, (tuple, list)) or len(move) != 2:
        raise ValueError("move must be a pair of (row, col)")

    row, col = move
    if isinstance(row, bool) or isinstance(col, bool):
        raise ValueError("row and col must be integers")
    if not isinstance(row, Integral) or not isinstance(col, Integral):
        raise ValueError("row and col must be integers")

    row = int(row)
    col = int(col)
    if not (0 <= row < size and 0 <= col < size):
        raise ValueError(f"move {(row, col)} is out of bounds for board size {size}")
    return row, col


def _validate_index(index, size: int) -> int:
    if isinstance(index, bool) or not isinstance(index, Integral):
        raise ValueError("index must be an integer")

    index = int(index)
    if not (0 <= index < size * size):
        raise ValueError(f"index {index} is out of bounds for board size {size}")
    return index


class Code:
    def __init__(self, board: Board):
        self.board = board
        self.size = self.board.size
        self.cnt_player = self.board.cnt_player
        self.oppo_player = 1 if self.cnt_player == 2 else 2

        self.code = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(3)]
        self.code[2] = [
            [1 if self.cnt_player == 1 else 0 for _ in range(self.size)]
            for _ in range(self.size)
        ]

        for i in range(self.size):
            for j in range(self.size):
                stone = self.board.board[i][j]
                if stone == self.cnt_player:
                    self.code[0][i][j] = 1
                elif stone == self.oppo_player:
                    self.code[1][i][j] = 1

    def to_numpy(self) -> np.ndarray:
        return np.asarray(self.code, dtype=np.float32)

    def move_to_index(self, move: tuple[int, int]) -> int:
        row, col = _validate_move(move, self.size)
        return row * self.size + col

    def index_to_move(self, index: int) -> tuple[int, int]:
        index = _validate_index(index, self.size)
        return (index // self.size, index % self.size)


def encoder(board: Board):
    """Return the encoded board container."""
    return Code(board)


def encode_board(board: Board) -> np.ndarray:
    """Return a float32 array with shape (3, board_size, board_size)."""
    return encoder(board).to_numpy()


def get_code(board: Board) -> np.ndarray:
    """Backward-compatible alias for encode_board."""
    return encode_board(board)


def legal_move_mask(board: Board, flatten: bool = True) -> np.ndarray:
    size = board.size
    mask_list = [
        [1 if board.board[i][j] == 0 else 0 for j in range(size)]
        for i in range(size)
    ]
    policy_mask = np.asarray(mask_list, dtype=np.float32)
    if flatten:
        return policy_mask.reshape(-1)
    return policy_mask
