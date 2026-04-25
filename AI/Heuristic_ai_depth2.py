# File name : Heuristic_ai_depth2.py
# Content: Enhanced Heuristic AI with 2-ply minimax search using incremental evaluation
# and candidate pruning for speed.

import random
from board import Board
from AI.base import BaseAI
from typing import Optional, Tuple, List


class HeuristicAIDepth2(BaseAI):
    """
    A 2-ply minimax AI for Gomoku.
    It uses the same pattern recognition as HeuristicAI, but looks one opponent
    reply ahead to better balance attack and defense.
    """

    def __init__(self, board, player: int):
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

    # ----------------------------------------------------------------------
    # Main move selection: 2-ply minimax with incremental scoring
    # ----------------------------------------------------------------------
    def get_move(self) -> Optional[Tuple[int, int]]:
        best_score = float('-inf')
        best_moves: List[Tuple[int, int]] = []
        opponent = 3 - self.player

        # Get candidates (empty cells near existing pieces)
        candidates = self._get_candidates(radius=2)
        if not candidates:
            return None

        # Evaluate the current board from AI's perspective (baseline total)
        base_total = (self._evaluate_board(for_player=self.player) -
                      self._evaluate_board(for_player=opponent))

        # Try every candidate move for the AI
        for r_ai, c_ai in candidates:
            # Simulate AI's move
            self.board.board[r_ai][c_ai] = self.player
            if self.board.check_win(self.player, [r_ai, c_ai]):
                self.board.board[r_ai][c_ai] = 0  # Undo move
                return (r_ai, c_ai)  # Immediate win
            gain_ai = self._score_move_one_step(r_ai, c_ai, for_player=self.player)
            after_ai_total = base_total + gain_ai

            # Now opponent tries to minimize AI's total
            worst_for_ai = float('inf')
            for r_opp, c_opp in candidates:
                if self.board.board[r_opp][c_opp] == 0:
                    self.board.board[r_opp][c_opp] = opponent
                    gain_opp = self._score_move_one_step(r_opp, c_opp, for_player=opponent)
                    after_opp_total = after_ai_total - gain_opp  # opponent's gain hurts AI
                    if after_opp_total < worst_for_ai:
                        worst_for_ai = after_opp_total
                    self.board.board[r_opp][c_opp] = 0

            # Undo AI's move
            self.board.board[r_ai][c_ai] = 0

            # AI picks the move that gives the highest worst-case score
            if worst_for_ai > best_score:
                best_score = worst_for_ai
                best_moves = [(r_ai, c_ai)]
            elif worst_for_ai == best_score:
                best_moves.append((r_ai, c_ai))

        return random.choice(best_moves) if best_moves else None

    # ----------------------------------------------------------------------
    # Candidate pruning (only cells near existing stones)
    # ----------------------------------------------------------------------
    def _get_candidates(self, radius: int = 2) -> List[Tuple[int, int]]:
        cand = set()
        s = self.board.size
        for r in range(s):
            for c in range(s):
                if self.board.board[r][c] != 0:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < s and 0 <= nc < s and self.board.board[nr][nc] == 0:
                                cand.add((nr, nc))
        if not cand:  # completely empty board
            return [(s // 2, s // 2)]
        return list(cand)

    # ----------------------------------------------------------------------
    # Line extraction and pattern evaluation (same as HeuristicAI)
    # ----------------------------------------------------------------------
    def _get_line_string(self, row: int, col: int, dr: int, dc: int) -> str:
        line = ''
        size = self.board.size
        r, c = row, col
        while 0 <= r - dr < size and 0 <= c - dc < size:
            r -= dr
            c -= dc
        while 0 <= r < size and 0 <= c < size:
            line += str(self.board.board[r][c])
            r += dr
            c += dc
        return line

    def _evaluate_line(self, line: str, patterns: dict) -> int:
        total = 0
        for pattern, feature in patterns.items():
            if pattern in line:
                total += (self.shape_score["potential"].get(feature, 0) +
                          self.shape_score["sleep"].get(feature, 0))
        return total

    # ----------------------------------------------------------------------
    # Full‑board evaluation (used once at root to get baseline)
    # ----------------------------------------------------------------------
    def _evaluate_board(self, for_player: Optional[int] = None) -> int:
        if for_player is None:
            for_player = self.player

        if for_player == 1:
            patterns = {
                '0110': '活二', '01110': '活三', '011110': '活四',
                '2110': '眠二', '0112': '眠二', '21110': '眠三',
                '01112': '眠三', '211110': '眠四', '011112': '眠四',
                '11111': '五',
            }
        else:
            patterns = {
                '0220': '活二', '02220': '活三', '022220': '活四',
                '1220': '眠二', '0221': '眠二', '12220': '眠三',
                '02221': '眠三', '122220': '眠四', '022221': '眠四',
                '22222': '五',
            }

        total = 0
        size = self.board.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            if dr == 0 and dc == 1:  # Horizontal
                for row in range(size):
                    line = self._get_line_string(row, 0, dr, dc)
                    total += self._evaluate_line(line, patterns)
            elif dr == 1 and dc == 0:  # Vertical
                for col in range(size):
                    line = self._get_line_string(0, col, dr, dc)
                    total += self._evaluate_line(line, patterns)
            elif dr == 1 and dc == 1:  # Main diagonal (\)
                for row in range(size):
                    line = self._get_line_string(row, 0, dr, dc)
                    total += self._evaluate_line(line, patterns)
                for col in range(1, size):
                    line = self._get_line_string(0, col, dr, dc)
                    total += self._evaluate_line(line, patterns)
            elif dr == 1 and dc == -1:  # Anti-diagonal (/)
                for row in range(size):
                    line = self._get_line_string(row, size - 1, dr, dc)
                    total += self._evaluate_line(line, patterns)
                for col in range(size - 1):
                    line = self._get_line_string(0, col, dr, dc)
                    total += self._evaluate_line(line, patterns)
        return total

    # ----------------------------------------------------------------------
    # Incremental move score (gain in attack + weighted defense)
    # ----------------------------------------------------------------------
    def _score_move_one_step(self, row: int, col: int, weight: float = 0.8,
                             for_player: int = None) -> float:
        if for_player is None:
            for_player = self.player
        opponent = 3 - for_player

        # Choose pattern dictionaries based on the player we are scoring
        if for_player == 1:
            my_patterns = {
                '0110': '活二', '01110': '活三', '011110': '活四',
                '2110': '眠二', '0112': '眠二', '21110': '眠三',
                '01112': '眠三', '211110': '眠四', '011112': '眠四',
                '11111': '五',
            }
            op_patterns = {
                '0220': '活二', '02220': '活三', '022220': '活四',
                '1220': '眠二', '0221': '眠二', '12220': '眠三',
                '02221': '眠三', '122220': '眠四', '022221': '眠四',
                '22222': '五',
            }
        else:
            my_patterns = {
                '0220': '活二', '02220': '活三', '022220': '活四',
                '1220': '眠二', '0221': '眠二', '12220': '眠三',
                '02221': '眠三', '122220': '眠四', '022221': '眠四',
                '22222': '五',
            }
            op_patterns = {
                '0110': '活二', '01110': '活三', '011110': '活四',
                '2110': '眠二', '0112': '眠二', '21110': '眠三',
                '01112': '眠三', '211110': '眠四', '011112': '眠四',
                '11111': '五',
            }

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        # Baseline scores before placing any piece
        old_my = 0
        old_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            old_my += self._evaluate_line(line, my_patterns)
            old_op += self._evaluate_line(line, op_patterns)

        # Gain when for_player occupies the cell
        self.board.board[row][col] = for_player
        new_my = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_my += self._evaluate_line(line, my_patterns)
        attack_gain = new_my - old_my

        # Gain when opponent occupies the cell (defensive importance)
        self.board.board[row][col] = opponent
        new_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_op += self._evaluate_line(line, op_patterns)
        defense_gain = new_op - old_op

        # Restore empty cell
        self.board.board[row][col] = 0

        return attack_gain + weight * defense_gain