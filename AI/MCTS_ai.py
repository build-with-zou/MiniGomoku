# File name: MCTS_ai.py
# Content: MCTS AI for Gomoku game with forced-threat detection.

import math
import random

from AI.MCTS_node import MCTSNode
from AI.base import BaseAI


class MCTS_AI(BaseAI):
    def __init__(self, board, player=None, times=1000):
        super().__init__(board, player)
        self.player = player
        self.opponent = 2 if player == 1 else 1
        self.times = times

    def _apply_move(self, board, move, player):
        return board.apply_move(player, list(move))

    # Compulsory defensive helpers.
    def _get_line_string(self, row, col, dr, dc):
        line = ""
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

    def _has_forced_offense(self, player, row, col):
        piece = str(player)
        opp_piece = str(3 - player)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if "0" + piece * 4 + "0" in line:
                return True
            if opp_piece + piece * 4 + "0" in line or "0" + piece * 4 + opp_piece in line:
                return True
        live_three_count = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if "0" + piece * 3 + "0" in line:
                live_three_count += 1
                if live_three_count >= 2:
                    return True
        return False

    def _has_live_four(self, player, row, col):
        piece = str(player)
        pattern = "0" + piece * 4 + "0"
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if pattern in self._get_line_string(row, col, dr, dc):
                return True
        return False

    def _has_double_three(self, player, row, col):
        piece = str(player)
        count = 0
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line = self._get_line_string(row, col, dr, dc)
            if "0" + piece * 3 + "0" in line:
                count += 1
                if count >= 2:
                    return True
        return False

    def _find_immediate_win(self):
        for r, c in self.board.legal_moves():
            self.board.board[r][c] = self.player
            try:
                if self.board.check_win(self.player, (r, c)):
                    return (r, c)
            finally:
                self.board.board[r][c] = 0
        return None

    def _get_forced_defensive_moves(self):
        forced = []
        for r, c in self.board.legal_moves():
            self.board.board[r][c] = self.opponent
            try:
                if self.board.check_win(self.opponent, (r, c)):
                    forced.append((r, c))
                elif self._has_live_four(self.opponent, r, c) or self._has_double_three(self.opponent, r, c):
                    forced.append((r, c))
            finally:
                self.board.board[r][c] = 0
        return forced

    def _select_child(self, node):
        best_score = -float("inf")
        best_node = None
        for child in node.children.values():
            score = self.uct_score(child)
            if score > best_score:
                best_score = score
                best_node = child
        return best_node

    def get_move(self):
        if self.board.is_full():
            return None

        win_move = self._find_immediate_win()
        if win_move is not None:
            return win_move

        forced = self._get_forced_defensive_moves()
        if forced:
            return random.choice(forced)

        root = MCTSNode(
            parent=None,
            pos=None,
            player=3 - self.player,
            player_to_move=self.player,
            state_key=self.board.create_key(),
        )
        root.untried_moves = self.get_candidate_moves(self.board)
        if not root.untried_moves:
            return None

        for _ in range(self.times):
            sim_board = self.board.clone()
            node = root

            while node.children and node.is_fully_expanded():
                node = self._select_child(node)
                if node is None:
                    break
                if not self._apply_move(sim_board, node.action, node.player):
                    break

            if node is None:
                continue

            if node.untried_moves:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                mover = node.player_to_move if node.player_to_move in (1, 2) else self.player
                if not self._apply_move(sim_board, move, mover):
                    continue
                child = MCTSNode(
                    parent=node,
                    pos=move,
                    player=mover,
                    player_to_move=3 - mover,
                    state_key=sim_board.create_key(),
                )
                child.untried_moves = self.get_candidate_moves(sim_board)
                node.children[move] = child
                node = child

            reward = self.rollout(sim_board, node.player_to_move or self.player)
            self.backpropagate(node, reward)

        if not root.children:
            return random.choice(root.untried_moves) if root.untried_moves else random.choice(self.board.legal_moves())

        best_visit = max(child.visits for child in root.children.values())
        best_moves = [move for move, child in root.children.items() if child.visits == best_visit]
        return random.choice(best_moves)

    def uct_score(self, node):
        if node.visits == 0:
            return float("inf")
        parent_visits = max(1, node.parent.visits if node.parent else 1)
        exploitation = node.value / node.visits
        exploration = math.sqrt(2 * math.log(parent_visits) / node.visits)
        return exploitation + exploration

    def rollout(self, board, player_to_move):
        """Simulate a random playout from the current board state."""
        start_player = player_to_move
        current = player_to_move
        while True:
            legal = self.get_candidate_moves(board)
            if not legal:
                return 0.0
            move = random.choice(legal)
            if not self._apply_move(board, move, current):
                return 0.0
            if board.check_win(current, move):
                return 1.0 if current == start_player else -1.0
            if board.is_full():
                return 0.0
            current = 3 - current

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            reward = -reward
            node = node.parent

    def get_candidate_moves(self, board, radius=2):
        candidates = set()
        for r in range(board.size):
            for c in range(board.size):
                if board.board[r][c] != 0:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < board.size and 0 <= nc < board.size:
                                if board.board[nr][nc] == 0:
                                    candidates.add((nr, nc))
        if not candidates:
            if board.is_empty():
                candidates.add((board.size // 2, board.size // 2))
            else:
                candidates.update(board.legal_moves())
        return list(candidates)

