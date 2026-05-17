# File name: MCTS_ai.py
# Content: MCTS AI for Gomoku game (with forced threat detection)

import math
import random
from board import Board
from AI.base import BaseAI
from AI.MCTS_node import MCTSNode


class MCTS_AI(BaseAI):
    def __init__(self, board, player=None, times=1000):
        super().__init__(board, player)
        self.player = player
        self.opponent = 2 if player == 1 else 1
        self.times = times

    # Compulsory defensive (Transplanted from HeuristicAIDepth)
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

    def _has_forced_offense(self, player, row, col):
        piece = str(player)
        opp_piece = str(3 - player)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if '0' + piece * 4 + '0' in line:
                return True
            if opp_piece + piece * 4 + '0' in line or '0' + piece * 4 + opp_piece in line:
                return True
        live_three_count = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if '0' + piece * 3 + '0' in line:
                live_three_count += 1
                if live_three_count >= 2:
                    return True
        return False

    def _has_live_four(self, player, row, col):
        piece = str(player)
        pattern = '0' + piece * 4 + '0'
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if pattern in self._get_line_string(row, col, dr, dc):
                return True
        return False

    def _has_double_three(self, player, row, col):
        piece = str(player)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        count = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            if '0' + piece * 3 + '0' in line:
                count += 1
                if count >= 2:
                    return True
        return False

    def _find_immediate_win(self):
        """Check if the AI can win in the next move, and return that move if it exists."""
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.board[r][c] != 0:
                    continue
                self.board.board[r][c] = self.player
                if self.board.check_win(self.player, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c)
                self.board.board[r][c] = 0
        return None

    def _get_forced_defensive_moves(self):
        """Return a list of moves that must be defended immediately (opponent's immediate win, live four, double three)."""
        forced = []
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.board[r][c] != 0:
                    continue
                self.board.board[r][c] = self.opponent
                # Opponent's immediate win
                if self.board.check_win(self.opponent, [r, c]):
                    forced.append((r, c))
                # Opponent forms a live four or double three, which we must block.
                elif self._has_live_four(self.opponent, r, c) or \
                     self._has_double_three(self.opponent, r, c):
                    forced.append((r, c))
                self.board.board[r][c] = 0
        return forced

    # MCTS Implementation (with forced threat detection)

    def get_move(self):
        # 1. If I have an immediate winning move, take it
        win_move = self._find_immediate_win()
        if win_move is not None:
            return win_move

        # 2. If the opponent has a forced threat, block it
        forced = self._get_forced_defensive_moves()
        if forced:
            return random.choice(forced)

        # 3. Otherwise, start MCTS
        root = MCTSNode(player=self.opponent)  # Opponent just moved, now it's AI's turn
        root.untried_moves = self.get_candidate_moves(self.board)

        for _ in range(self.times):
            sim_board = self.board.clone()
            # First: Selection and Expansion
            node = self.select(root)
            # Second: If the node is not fully expanded, expand it
            if not node.is_fully_expanded():
                node = self.expand(node, sim_board)

            current_player = 3 - node.player      # The actual next player after expansion
            # Third: Simulation (Rollout)
            reward = self.rollout(sim_board, current_player)
            # Fourth: Backpropagate the result up the tree
            self.backpropagate(node, reward)

        best_move = max(root.children, key=lambda m: root.children[m].visits)
        return best_move

    def uct_score(self, node):
        if node.visits == 0:
            return float('inf')
        parent_visits = node.parent.visits
        # The total score is the sum of exploitation and exploration terms
        exploitation = node.value / node.visits
        exploration = math.sqrt(2 * math.log(parent_visits) / node.visits) # You can change the exploration constant (2) to something else if you want to adjust the balance between exploration and exploitation
        return exploitation + exploration

    def select(self, node):
        """Select a child node to explore based on UCT score, until we reach a node that is not fully expanded."""
        while node.is_fully_expanded():
            best_score = -float('inf')
            best_node = None
            for child in node.children.values():
                score = self.uct_score(child)
                if score > best_score:
                    best_score = score
                    best_node = child
            node = best_node
        return node

    def expand(self, node, board):
        """Expand a node by adding a new child node for one of its untried moves."""
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)
        current_player = 3 - node.player
        board.place(current_player, list(move))
        child = MCTSNode(parent=node, pos=move, player=current_player)
        child.untried_moves = self.get_candidate_moves(board)
        node.children[move] = child
        return child

    def rollout(self, board, player):
        """Simulate a random playout from the current board state until the game ends, and return the reward for the AI player."""
        sim_board = board.clone()
        current = player
        while True:
            legal = self.get_candidate_moves(sim_board)
            if not legal:
                return 0.0
            move = random.choice(legal)
            sim_board.place(current, list(move))
            if sim_board.check_win(current, move):
                return 1.0 if current == player else -1.0
            if sim_board.is_full():
                return 0.0
            current = 3 - current

    def backpropagate(self, node, reward):
        """Backpropagate the reward up the tree, updating the value and visit count of each node along the path."""
        while node is not None:
            node.visits += 1
            node.value += reward
            reward = -reward
            node = node.parent

    def get_candidate_moves(self, board, radius=2):
        """This function is to cut down the branching factor by only considering empty cells that are within a certain radius of existing pieces."""
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
            candidates.add((board.size // 2, board.size // 2))
        return list(candidates)