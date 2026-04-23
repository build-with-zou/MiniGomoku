from abc import ABC, abstractmethod 
class BaseAI(ABC):
    """
    Base class for AI players in the Gomoku game.
    All AI implementations should inherit from this class and implement the `get_move` method.
    """

    def __init__(self, board, player):
        
        """
        Initialize the AI player.
        """
        self.board = board
        self.player = player

    @abstractmethod
    def get_move(self) -> tuple[int, int] | None:
        """
        Core method to determine the AI's move based on the current state of the board.
        All AI implementations must override this method to provide their move logic.
        :return: A tuple (row, col) representing the AI's chosen move.
                 If no moves are available (board is full), return None.
        """
        pass

    def make_move(self) -> bool:
        move = self.get_move()
        if move is not None:
            return self.board.place(self.player, list(move))
        return False

    