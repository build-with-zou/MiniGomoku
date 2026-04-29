# File name: Heuristic_ai_depth.py
# Content: Balanced heuristic AI with configurable depth, incremental evaluation,
#          alpha-beta pruning, quiescence search, and intelligent threat handling.

import random
from board import Board
from AI.base import BaseAI
from typing import Optional, Tuple, List
from AI.pattern import Pattern

class HeuristicAIDepth(BaseAI):
    def __init__(self, board, player: int, depth: int = 3):
        super().__init__(board, player)
        self.pattern = Pattern(player)
        self.opponent = 2 if player == 1 else 1
        self.depth = depth
        self.shape_score = self.pattern.pattern_score

    # ---------- Main entry ----------
    def get_move(self) -> Optional[Tuple[int, int]]:
        if self.board.is_empty():
            return (self.board.size // 2, self.board.size // 2)

        # 1. Check immediate win
        win_move = self._find_immediate_win(self.player)
        if win_move is not None:
            return win_move

        # 2. Check opponent's forced threats (only direct win or live-four/double-three)
        forced_moves = self._get_forced_defensive_moves()
        if forced_moves:
            return random.choice(forced_moves)

        # 3. Normal search
        base_score = (self._evaluate_board(self.player) -
                      self._evaluate_board(self.opponent))
        move, _ = self.minimax(depth=self.depth,
                               alpha=float('-inf'), beta=float('inf'),
                               maximizing=True, current_score=base_score)
        return move

    def make_move(self) -> bool:
        move = self.get_move()
        if move is not None:
            return self.board.place(self.player, list(move))
        return False

    # ---------- Immediate win detection ----------
    def _find_immediate_win(self, player: int) -> Optional[Tuple[int, int]]:
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.board[r][c] != 0:
                    continue
                self.board.board[r][c] = player
                if self.board.check_win(player, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c)
                self.board.board[r][c] = 0
        return None

    # ---------- Forced defensive moves ----------
    def _get_forced_defensive_moves(self) -> List[Tuple[int, int]]:
        forced = []
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.board[r][c] != 0:
                    continue
                self.board.board[r][c] = self.opponent
                # Direct win for opponent
                if self.board.check_win(self.opponent, [r, c]):
                    forced.append((r, c))
                # Opponent creates live-four or double-three (unstoppable)
                elif self._has_live_four(self.opponent, r, c) or \
                     self._has_double_three(self.opponent, r, c):
                    forced.append((r, c))
                self.board.board[r][c] = 0
        return forced

    # ---------- Offensive threat detection (for AI's moves) ----------
    def _has_forced_offense(self, player: int, row: int, col: int) -> bool:
        """Check if the player creates a winning threat (live-four, rush-four, or double-three)."""
        piece = str(player)
        opp_piece = str(3 - player)
        directions = [(0,1), (1,0), (1,1), (1,-1)]

        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            # Live four
            if '0' + piece*4 + '0' in line:
                return True
            # Rush four (sleep four)
            if opp_piece + piece*4 + '0' in line or '0' + piece*4 + opp_piece in line:
                return True

        # Double three (two different directions with open three)
        live_three_count = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if '0' + piece*3 + '0' in line:
                live_three_count += 1
                if live_three_count >= 2:
                    return True
        return False

    # ---------- Special defensive checks ----------
    def _has_live_four(self, player: int, row: int, col: int) -> bool:
        piece = str(player)
        pattern = '0' + piece*4 + '0'
        for dr, dc in [(0,1),(1,0),(1,1),(1,-1)]:
            if pattern in self._get_line_string(row, col, dr, dc):
                return True
        return False

    def _has_double_three(self, player: int, row: int, col: int) -> bool:
        piece = str(player)
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        count = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if '0' + piece*3 + '0' in line:
                count += 1
                if count >= 2:
                    return True
        return False

    # ---------- Candidate moves ----------
    def get_candidate(self, radius: int = 2) -> List[Tuple[int, int]]:
        candidates = set()
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.board[row][col] != 0:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            r, c = row + dr, col + dc
                            if 0 <= r < self.board.size and 0 <= c < self.board.size and self.board.board[r][c] == 0:
                                candidates.add((r, c))
        return list(candidates)

    # ---------- Line and evaluation ----------
    def _get_line_string(self, row, col, dr, dc):
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

    def _evaluate_line(self, line, patterns):
        total = 0
        for pattern, feature in patterns.items():
            if pattern in line:
                total += (self.shape_score["potential"].get(feature, 0) +
                          self.shape_score["sleep"].get(feature, 0))
        return total

    def _evaluate_board(self, for_player=None):
        if for_player is None:
            for_player = self.player
        patterns = self.pattern.get_pattern(for_player)
        total = 0
        size = self.board.size
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        for dr, dc in directions:
            if dr == 0 and dc == 1:
                for row in range(size):
                    total += self._evaluate_line(self._get_line_string(row, 0, dr, dc), patterns)
            elif dr == 1 and dc == 0:
                for col in range(size):
                    total += self._evaluate_line(self._get_line_string(0, col, dr, dc), patterns)
            elif dr == 1 and dc == 1:
                for row in range(size):
                    total += self._evaluate_line(self._get_line_string(row, 0, dr, dc), patterns)
                for col in range(1, size):
                    total += self._evaluate_line(self._get_line_string(0, col, dr, dc), patterns)
            elif dr == 1 and dc == -1:
                for row in range(size):
                    total += self._evaluate_line(self._get_line_string(row, size-1, dr, dc), patterns)
                for col in range(size-1):
                    total += self._evaluate_line(self._get_line_string(0, col, dr, dc), patterns)
        return total

    # ---------- Incremental move score ----------
    def _score_move_one_step(self, row, col, for_player, weight=0.5):
        my_patterns = self.pattern.get_pattern(for_player)
        op_patterns = self.pattern.get_pattern(3 - for_player)
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        old_my = 0
        old_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            old_my += self._evaluate_line(line, my_patterns)
            old_op += self._evaluate_line(line, op_patterns)

        self.board.board[row][col] = for_player
        new_my = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_my += self._evaluate_line(line, my_patterns)
        attack_gain = new_my - old_my

        self.board.board[row][col] = 3 - for_player
        new_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_op += self._evaluate_line(line, op_patterns)
        defense_gain = new_op - old_op

        self.board.board[row][col] = 0
        return attack_gain + weight * defense_gain

    # ---------- Minimax with alpha-beta ----------
    def minimax(self, depth, alpha, beta, maximizing, current_score=0):
        if depth == 0 or self.board.is_full():
            score = self.quiescence_search(alpha, beta, maximizing, current_score)
            return None, score

        candidates = self.get_candidate(radius=2)

        if maximizing:
            best_move = []
            max_eval = -float('inf')
            for r, c in candidates:
                self.board.board[r][c] = self.player
                if self.board.check_win(self.player, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c), float('inf')
                if self._has_forced_offense(self.player, r, c):
                    self.board.board[r][c] = 0
                    return (r, c), float('inf')

                gain = self._score_move_one_step(r, c, self.player)
                new_score = current_score + gain
                _, score = self.minimax(depth-1, alpha, beta, False, new_score)
                self.board.board[r][c] = 0

                if score > max_eval:
                    max_eval = score
                    best_move = [(r, c)]
                elif score == max_eval:
                    best_move.append((r, c))
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return random.choice(best_move), max_eval
        else:
            best_move = []
            min_eval = float('inf')
            opponent = 3 - self.player
            for r, c in candidates:
                self.board.board[r][c] = opponent
                if self.board.check_win(opponent, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c), float('-inf')
                if self._has_live_four(opponent, r, c) or self._has_double_three(opponent, r, c):
                    self.board.board[r][c] = 0
                    return (r, c), float('-inf')

                gain = self._score_move_one_step(r, c, opponent)
                new_score = current_score - gain
                _, score = self.minimax(depth-1, alpha, beta, True, new_score)
                self.board.board[r][c] = 0

                if score < min_eval:
                    min_eval = score
                    best_move = [(r, c)]
                elif score == min_eval:
                    best_move.append((r, c))
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return random.choice(best_move), min_eval

    # ---------- Quiescence search ----------
    def quiescence_search(self, alpha, beta, maximizing, current_score, max_qdepth=2):
        stand_pat = current_score
        if maximizing:
            if stand_pat >= beta: return beta
            if stand_pat > alpha: alpha = stand_pat
        else:
            if stand_pat <= alpha: return alpha
            if stand_pat < beta: beta = stand_pat

        if max_qdepth == 0:
            return stand_pat

        player = self.player if maximizing else self.opponent
        forced_moves = set()
        candidates = self.get_candidate(radius=2)

        for r, c in candidates:
            if self.board.board[r][c] != 0: continue
            self.board.board[r][c] = player
            if self.board.check_win(player, [r, c]) or self._has_forced_offense(player, r, c):
                forced_moves.add((r, c))
            self.board.board[r][c] = 0

            opponent = 3 - player
            self.board.board[r][c] = opponent
            if self.board.check_win(opponent, [r, c]) or self._has_live_four(opponent, r, c) or self._has_double_three(opponent, r, c):
                forced_moves.add((r, c))
            self.board.board[r][c] = 0

        if maximizing:
            for r, c in forced_moves:
                self.board.board[r][c] = self.player
                if self.board.check_win(self.player, [r, c]):
                    self.board.board[r][c] = 0
                    return float('inf')
                gain = self._score_move_one_step(r, c, self.player)
                new_score = current_score + gain
                score = self.quiescence_search(alpha, beta, False, new_score, max_qdepth-1)
                self.board.board[r][c] = 0
                alpha = max(alpha, score)
                if alpha >= beta: break
            return alpha
        else:
            for r, c in forced_moves:
                self.board.board[r][c] = self.opponent
                if self.board.check_win(self.opponent, [r, c]):
                    self.board.board[r][c] = 0
                    return float('-inf')
                gain = self._score_move_one_step(r, c, self.opponent)
                new_score = current_score - gain
                score = self.quiescence_search(alpha, beta, True, new_score, max_qdepth-1)
                self.board.board[r][c] = 0
                beta = min(beta, score)
                if alpha >= beta: break
            return beta