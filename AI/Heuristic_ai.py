# ai/heuristic_ai.py
from AI.base import BaseAI
from typing import Optional, Tuple

class HeuristicAI(BaseAI):
    """
    This is a simple heuristic AI for Gomoku that evaluates potential moves based on pattern recognition and scoring.
    Based on pattern scoring, this heuristic AI evaluates potential moves by analyzing the board's lines for both offensive and defensive opportunities. 
    It considers various patterns (like "活二", "眠三", etc.) and assigns scores to them,allowing it to make informed decisions that balance attack and defense.
    """

    def __init__(self, board, player: int):
        """
        Initialize the heuristic AI.
        :param board: Board object (instance of the Board class)
        :param player: Player number that the AI represents (1 or 2)
        """
        super().__init__(board, player)  
        # define pattern scores for both potential and sleep patterns
        self.shape_score = {
            "potential": {
                '活二': 1,
                '活三': 10,
                '活四': 100,
                '五': 10000,
            },
            "sleep": {
                '眠二': 0,
                '眠三': 5,
                '眠四': 50,
            }
        }

    def get_move(self) -> Optional[Tuple[int, int]]:
        """
        Realize the get_move method to evaluate all possible moves and return the one with the highest score.
        Return : A tuple (row, col) representing the AI's chosen move, or None if no moves are available.
        """
        best_score = float('-inf')
        best_move = None
        size = self.board.size
        for r in range(size):
            for c in range(size):
                if self.board.board[r][c] == 0:  # 仅考虑空位
                    score = self._score_move(r, c)
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        return best_move

    # ----------------------------------------------------------------------
    # Below are helper methods for evaluating the board and scoring moves based on patterns. These methods are used internally by the get_move method to determine the best move for the AI.
    # ----------------------------------------------------------------------

    def _get_line_string(self, row: int, col: int, dr: int, dc: int) -> str:
        """
        Get the string representation of a line of pieces starting from (row, col) in the direction (dr, dc).
        '0' represents an empty space, '1' represents player 1, and '2' represents player 2.

        """
        line = ''
        size = self.board.size
        # Move to the starting end of the line
        r, c = row, col
        while 0 <= r - dr < size and 0 <= c - dc < size:
            r -= dr
            c -= dc

        # Traverse the entire line from the starting end
        while 0 <= r < size and 0 <= c < size:
            line += str(self.board.board[r][c])
            r += dr
            c += dc
        return line

    def _evaluate_line(self, line: str, patterns: dict) -> int:
        """
        According to the given pattern dictionary, score a line.
        :param line: The line string
        :param patterns: The pattern dictionary, e.g., {'0110': '活二', ...}
        :return: The total score for the line based on the patterns it contains.
        """
        total_score = 0
        for pattern, feature in patterns.items():
            if pattern in line:
                total_score += (self.shape_score["potential"].get(feature, 0) +
                                self.shape_score["sleep"].get(feature, 0))
        return total_score

    def _evaluate_board(self, for_player: Optional[int] = None) -> int:
        """
        Evaluate the entire board for the specified player (or the AI itself if None) by checking all lines in four directions and summing their scores based on pattern recognition.
        :param for_player: The player number to evaluate, defaults to the AI itself
        :return: The total score for the board
        """
        if for_player is None:
            for_player = self.player

        # Set the pattern dictionary based on the player being evaluated
        if for_player == 1:
            patterns = {
                '0110': '活二',
                '01110': '活三',
                '011110': '活四',
                '2110': '眠二',
                '0112': '眠二',
                '21110': '眠三',
                '01112': '眠三',
                '211110': '眠四',
                '011112': '眠四',
                '11111': '五',
            }
        else:
            patterns = {
                '0220': '活二',
                '02220': '活三',
                '022220': '活四',
                '1220': '眠二',
                '0221': '眠二',
                '12220': '眠三',
                '02221': '眠三',
                '122220': '眠四',
                '022221': '眠四',
                '22222': '五',
            }

        total_score = 0
        size = self.board.size
        # Four directions: horizontal, vertical, main diagonal (\), and anti-diagonal (/)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            if dr == 0 and dc == 1:  # Horizontal
                for row in range(size):
                    line = self._get_line_string(row, 0, dr, dc)
                    total_score += self._evaluate_line(line, patterns)

            elif dr == 1 and dc == 0:  # Vertical
                for col in range(size):
                    line = self._get_line_string(0, col, dr, dc)
                    total_score += self._evaluate_line(line, patterns)

            elif dr == 1 and dc == 1:  # Main diagonal (\)
                for row in range(size):
                    line = self._get_line_string(row, 0, dr, dc)
                    total_score += self._evaluate_line(line, patterns)
                for col in range(1, size):
                    line = self._get_line_string(0, col, dr, dc)
                    total_score += self._evaluate_line(line, patterns)

            elif dr == 1 and dc == -1:  # Anti-diagonal (/)
                for row in range(size):
                    line = self._get_line_string(row, size - 1, dr, dc)
                    total_score += self._evaluate_line(line, patterns)
                for col in range(size - 1):
                    line = self._get_line_string(0, col, dr, dc)
                    total_score += self._evaluate_line(line, patterns)

        return total_score

    def _score_move(self, row: int, col: int) -> float:
        """
        Calculate the score of placing a piece at (row, col) by evaluating both the offensive potential and defensive necessity of that move. The score is a combination of the attack score (based on the AI's own patterns) and the defense score (based on the opponent's patterns), with a weight applied to the defense score to balance the AI's strategy between offense and defense.
        """
        weight = 0.8  # Defense weight to balance attack and defense
        opponent = 3 - self.player

        # Temporarily place the AI's piece to calculate the attack score
        self.board.board[row][col] = self.player
        attack_score = self._evaluate_board()
        # Temporarily place the opponent's piece to calculate the defense score
        self.board.board[row][col] = opponent
        defense_score = self._evaluate_board(for_player=opponent)
        # Restore the empty position
        self.board.board[row][col] = 0

        return attack_score + weight * defense_score