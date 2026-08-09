from __future__ import annotations

from typing import Optional


class Board:
    """Game board and rule source for Gomoku."""

    def __init__(self, size: int = 15):
        self.reset(size)

    def reset(self, size: Optional[int] = None):
        """Reset the board state. If size is given, resize the board too."""
        if size is not None:
            self.size = int(size)
        elif not hasattr(self, "size"):
            self.size = 15

        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.move_count = 0
        self.last_move: Optional[tuple[int, int]] = None
        self.current_player = 1
        self.cnt_player = self.current_player
        self.move_history: list[tuple[int, int, int]] = []

    def _rebuild_from_history(self, history):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.move_history = []
        self.move_count = 0
        self.last_move = None
        self.current_player = 1
        self.cnt_player = 1

        for row, col, player in history:
            self.board[row][col] = player
            self.move_history.append((row, col, player))
            self.move_count += 1
            self.last_move = (row, col)
            self.current_player = 3 - player
            self.cnt_player = self.current_player

    def _unpack_pos(self, pos):
        if pos is None:
            return None
        if isinstance(pos, (list, tuple)) and len(pos) == 2:
            row, col = pos
            return row, col
        return None

    def in_bounds(self, pos) -> bool:
        unpacked = self._unpack_pos(pos)
        if unpacked is None:
            return False
        row, col = unpacked
        return isinstance(row, int) and isinstance(col, int) and 0 <= row < self.size and 0 <= col < self.size

    def is_valid_player(self, player) -> bool:
        return player in (1, 2)

    def is_legal_move(self, pos) -> bool:
        unpacked = self._unpack_pos(pos)
        if unpacked is None or not self.in_bounds(unpacked):
            return False
        row, col = unpacked
        return self.board[row][col] == 0

    def legal_moves(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]

    def apply_move(self, player: int, pos) -> bool:
        """Apply a move if it is legal."""
        unpacked = self._unpack_pos(pos)
        if unpacked is None:
            return False
        row, col = unpacked
        if not (self.is_valid_player(player) and self.in_bounds((row, col))):
            return False
        if self.board[row][col] != 0:
            return False

        self.board[row][col] = player
        self.move_count += 1
        self.last_move = (row, col)
        self.current_player = 3 - player
        self.cnt_player = self.current_player
        self.move_history.append((row, col, player))
        return True

    def place(self, player: int, pos) -> bool:
        """Backward-compatible alias for apply_move."""
        return self.apply_move(player, pos)

    def undo_move(self, pos=None) -> bool:
        """Undo the last move, or undo the specified last move if pos is provided."""
        if not self.move_history:
            return False

        if pos is None:
            index = len(self.move_history) - 1
        else:
            unpacked = self._unpack_pos(pos)
            if unpacked is None:
                return False
            index = None
            for i in range(len(self.move_history) - 1, -1, -1):
                if self.move_history[i][:2] == unpacked:
                    index = i
                    break
            if index is None:
                return False

        remaining_history = self.move_history[:index] + self.move_history[index + 1 :]
        self._rebuild_from_history(remaining_history)
        return True

    def remove(self, pos=None):
        """Backward-compatible alias for undo_move."""
        return self.undo_move(pos)

    def check_win(self, player, pos):
        """Return True if player has five or more in a row through pos."""
        if not self.is_valid_player(player):
            return False
        unpacked = self._unpack_pos(pos)
        if unpacked is None or not self.in_bounds(unpacked):
            return False
        row, col = unpacked
        if self.board[row][col] != player:
            return False

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True
        return False

    def is_empty(self):
        return self.move_count == 0

    def is_full(self):
        return self.move_count >= self.size * self.size

    def print_board(self):
        print("  " + " ".join(f"{i + 1:2}" for i in range(self.size)))
        for i, row in enumerate(self.board):
            print(f"{i + 1:2} " + "  ".join(str(cell) for cell in row))

    def clone(self):
        """Deep copy the board and all bookkeeping state."""
        new_board = Board(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.move_count = self.move_count
        new_board.last_move = self.last_move
        new_board.current_player = self.current_player
        new_board.cnt_player = self.cnt_player
        new_board.move_history = self.move_history[:]
        return new_board

    def create_key(self):
        """Return a stable string key for the current board state."""
        flattened = "".join(str(cell) for row in self.board for cell in row)
        return f"{self.size}|{self.current_player}|{self.move_count}|{flattened}"
