from abc import ABC, abstractmethod


class BaseAI(ABC):
    """
    Base class for all player objects.
    The concrete player can be a human, a heuristic AI, MCTS, or a future RL agent.
    """

    def __init__(self, board, player):
        self.board = board
        self.player = player

    def set_board(self, board):
        """Rebind the player to a new board instance."""
        self.board = board

    def reset(self) -> None:
        """Reset any internal state. Stateless players can ignore this."""
        pass

    def observe_move(self, player, move) -> None:
        """Optional hook for future stateful agents to observe a move."""
        pass

    def on_game_end(self, result) -> None:
        """Optional hook called when a game finishes."""
        pass

    @abstractmethod
    def get_move(self) -> tuple[int, int] | None:
        """Return the next move as (row, col), or None if no move is available."""
        pass

    def make_move(self) -> bool:
        move = self.get_move()
        if move is None:
            return False

        if hasattr(self.board, "apply_move"):
            return self.board.apply_move(self.player, list(move))
        return self.board.place(self.player, list(move))

