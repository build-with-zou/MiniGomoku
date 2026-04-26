# File name: Heuristic_ai_depth3.py
# Content: Heuristic AI with depth 3 for Gomoku game
import random
from board import Board
from AI.base import BaseAI
from typing import Optional, Tuple, List

class HeuristicAIDepth(BaseAI):
    """
    A general heuristic AI for Gomoku that evaluates the board state and selects the best move based on a heuristic evaluation function.
    You can adjust the depth of the search and the evaluation function to create different levels of difficulty. 

    To ensure the efficiency of the search, the AI uses alpha-beta pruning to eliminate branches that won't influence the final decision.
    """
    def __init__(self, board, player: int,depth:int = 3):
        super().__init__(board,player)
        self.opponent = 2 if player == 1 else 1
        self.depth = depth
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

    # The basic funcion to get the best move for the AI
    def get_move(self) -> Tuple[int, int]:
        if self.board.is_empty():
            # If the board is empty, place the first piece in the center
            return (self.board.size // 2, self.board.size // 2)
        base_score = self._evaluate_board(self.player) - self._evaluate_board(self.opponent)
        move, _ = self.minimax(depth=self.depth, alpha=float('-inf'), beta=float('inf'), maximizing=True, current_score=base_score)
        return move

    def make_move(self):
        move = self.get_move()
        if move is not None:
            return self.board.place(self.player, list(move))
        return False

    # The heuristic evaluation function to evaluate the board state

    def get_candidate(self,radius: int = 2) -> List[Tuple[int, int]]:
        """
        Get candidate moves based on the current board state. 
        The function considers moves within a certain radius of existing pieces to reduce the search space.

        :param radius: The radius around existing pieces to consider for candidate moves.
        :return: A list of candidate moves (row, col).
        """
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
    
    def _score_move_one_step(self, row: int, col: int, for_player: int, weight: float = 0.8) -> float:
        """返回 for_player 在 (row,col) 落子的综合增益（进攻 + 防守）"""
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

        # 落子前两条线分
        old_my = 0
        old_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            old_my += self._evaluate_line(line, my_patterns)
            old_op += self._evaluate_line(line, op_patterns)

        # 玩家落子后的进攻增益
        self.board.board[row][col] = for_player
        new_my = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_my += self._evaluate_line(line, my_patterns)
        attack_gain = new_my - old_my

        # 对手落子后的防守增益
        self.board.board[row][col] = 3 - for_player  # 换成对手
        new_op = 0
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            new_op += self._evaluate_line(line, op_patterns)
        defense_gain = new_op - old_op

        self.board.board[row][col] = 0  # 恢复
        return attack_gain + weight * defense_gain          
                    
    
    # The minimax algorithm with alpha-beta pruning to evaluate the best move for the AI.
    def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool,current_score = 0, weight = 0.8):
        # The base case for the recursion: if we've reached the maximum depth or the board is full, evaluate the board and return the score.
        if depth == 0 or self.board.is_full():
            return None, current_score

        candidates = self.get_candidate(radius=2)

        if maximizing:  # The turn of the AI (Max)
            best_move = []
            max_eval = -float('inf')

            for r, c in candidates:
                self.board.board[r][c] = self.player
                gain = self._score_move_one_step(r, c, self.player)
                new_score = current_score + gain
                # Immediate win → return this move with the maximum score
                if self.board.check_win(self.player, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c), float('inf')

                # Recursively search the next level (opponent's turn)
                _, score = self.minimax(depth - 1, alpha, beta, False, new_score)
                self.board.board[r][c] = 0

                if score > max_eval:
                    max_eval = score
                    best_move = [(r, c)]
                elif score == max_eval:
                    best_move.append((r, c))

                alpha = max(alpha, score)
                if alpha >= beta:   # Cutoff: Opponent will avoid this path, so we can stop searching further down this branch
                    break

            return random.choice(best_move), max_eval

        else:  # The turn of the opponent (Min)
            best_move = []
            min_eval = float('inf')
            opponent = 3 - self.player

            for r, c in candidates:
                self.board.board[r][c] = opponent
                opponent_gain = self._score_move_one_step(r, c, opponent)
                new_score = current_score - opponent_gain

                if self.board.check_win(opponent, [r, c]):
                    self.board.board[r][c] = 0
                    return (r, c), float('-inf')

                _, score = self.minimax(depth - 1, alpha, beta, True, new_score)
                self.board.board[r][c] = 0

                if score < min_eval:
                    min_eval = score
                    best_move = [(r, c)]
                elif score == min_eval:
                    best_move.append((r, c))

                beta = min(beta, score)
                if alpha >= beta:   # Cutoff: AI will avoid this path, so we can stop searching further down this branch
                    break

            return random.choice(best_move), min_eval
    
        

