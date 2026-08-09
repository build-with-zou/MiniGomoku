# ai/heuristic_ai.py
import random

from AI.base import BaseAI
from AI.pattern import get_opponent_pattern_map, get_pattern_map
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
        self.opponent = 2 if player == 1 else 1
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
        Feature :When there are multiple moves with the same highest score, the AI will randomly select one of them to add variability to its playstyle.
        Return : A tuple (row, col) representing the AI's chosen move, or None if no moves are available.
        """
        if self.board.is_full():
            return None

        win_move = self._find_immediate_win(self.player)
        if win_move is not None:
            return win_move

        forced_moves = self._get_forced_defensive_moves()
        if forced_moves:
            return random.choice(forced_moves)

        best_score = float('-inf')
        best_move = []
        for r, c in self.board.legal_moves():
            score = self._score_move(r, c)
            if score > best_score:
                best_score = score
                best_move = [(r, c)]
            elif score == best_score:
                best_move.append((r, c))
        if best_move:
            return random.choice(best_move)
        return None

    def _find_immediate_win(self, player: int) -> Optional[Tuple[int, int]]:
        for row, col in self.board.legal_moves():
            self.board.board[row][col] = player
            try:
                if self.board.check_win(player, (row, col)):
                    return (row, col)
            finally:
                self.board.board[row][col] = 0
        return None

    def _get_forced_defensive_moves(self):
        forced = []
        for row, col in self.board.legal_moves():
            self.board.board[row][col] = self.opponent
            try:
                if self.board.check_win(self.opponent, (row, col)):
                    forced.append((row, col))
            finally:
                self.board.board[row][col] = 0
        return forced

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
        patterns = get_pattern_map(for_player)

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

    def _score_move(self, row: int, col: int, weight: float = 0.8, for_player: int = None) -> float:
        """
        Calculate the score of placing a piece at (row, col) by evaluating both the offensive potential and defensive necessity of that move. The score is a combination of the attack score (based on the AI's own patterns) and the defense score (based on the opponent's patterns), with a weight applied to the defense score to balance the AI's strategy between offense and defense.
        In an attempt to improve the efficiency,we only evaluate the lines that are directly affected by the potential move, rather than evaluating the entire board for each move. This optimization significantly reduces the computational overhead while still providing a comprehensive assessment of the move's impact on both offensive and defensive positions.
        """
        if for_player is None:
            for_player = self.player

        my_patterns = get_pattern_map(for_player)
        opponent_patterns = get_opponent_pattern_map(for_player)
        current_my_score = 0
        current_opponent_score = 0
        attack_score = 0
        defense_score = 0
        opponent = 3 - for_player  # Get the opponent's player number (1 or 2)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        original = self.board.board[row][col]
        if original != 0:
            return float('-inf')

        try:
            # Evaluate the current board state for the AI and opponent to establish a baseline score before simulating the move
            for dr, dc in directions:
                line = self._get_line_string(row, col, dr, dc)
                current_my_score += self._evaluate_line(line, my_patterns)
                current_opponent_score += self._evaluate_line(line, opponent_patterns)

            # Evaluate the AI's own patterns for attack
            self.board.board[row][col] = for_player
            for dr, dc in directions:
                line = self._get_line_string(row, col, dr, dc)
                attack_score += self._evaluate_line(line, my_patterns)

            # Evaluate the opponent's patterns for defense
            self.board.board[row][col] = opponent
            for dr, dc in directions:
                line = self._get_line_string(row, col, dr, dc)
                defense_score += self._evaluate_line(line, opponent_patterns)
        finally:
            self.board.board[row][col] = original

        return attack_score - current_my_score + weight * (defense_score - current_opponent_score)


            
