# File name: Heuristic_ai_depth3.py
# Content: Heuristic AI with depth 3 for Gomoku game
import random
from board import Board
from AI.base import BaseAI
from typing import Optional, Tuple, List
from AI.pattern import Pattern

class HeuristicAIDepth(BaseAI):
    """
    A general heuristic AI for Gomoku that evaluates the board state and selects the best move based on a heuristic evaluation function.
    You can adjust the depth of the search and the evaluation function to create different levels of difficulty. 

    To ensure the efficiency of the search, the AI uses alpha-beta pruning to eliminate branches that won't influence the final decision.
    """
    def __init__(self, board, player: int,depth:int = 3):
        super().__init__(board,player)
        self.pattern = Pattern(player)      
        self.opponent = 2 if player == 1 else 1
        self.depth = depth
        self.shape_score = self.pattern.pattern_score

    # The basic funcion to get the best move for the AI
    def get_move(self) -> Tuple[int, int]:
        if self.board.is_empty():
            # If the board is empty, place the first piece in the center
            return (self.board.size // 2, self.board.size // 2)
        
        force_moves = self.get_forced_moves()
        if force_moves:
            return random.choice(force_moves)
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
        patterns = self.pattern.get_pattern(for_player)

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
    
    def _score_move_one_step(self, row: int, col: int, for_player: int, weight: float = 0.5) -> float:
        """返回 for_player 在 (row,col) 落子的综合增益（进攻 + 防守）"""
        my_patterns = self.pattern.get_pattern(for_player)
        op_patterns = self.pattern.get_pattern(3 - for_player)  # 对手的模式字典

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
                    
    def _has_forced_threat(self, player, row, col):
        """
        检查 players 是否在落子 (row, col) 后形成了必杀威胁。
        返回 True 如果有任意一条线满足：
        - 活四 (011110)
        - 冲四 (011112 或 211110) 并且攻击方是先手（即下一步可直接连五，对方必须堵）
        - 双活三 (在两个不同方向上都形成活三)
        """
        # 代表攻击方的棋子符号
        piece = str(player)
        # 四个方向
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        
        for dr, dc in directions:
            line = self._get_line_string(row, col, dr, dc)
            
            # 1. 检查活四：攻击方棋子形成 011110
            pattern_live4 = '0' + piece*4 + '0'
            if pattern_live4 in line:
                return True
                
            # 2. 检查冲四（眠四）：攻击方形成 211110 或 011112
            #    注意这里的 2 是对手的棋子（或边界被视为墙，但线已经包含边界），
            #    线中对手棋子就是 '2' 或 '1'(如果 player=2,对手就是1)
            opponent_piece = '2' if player == 1 else '1'
            
            # 冲四类型1: 211110
            pattern_rush4_a = opponent_piece + piece*4 + '0'
            if pattern_rush4_a in line:
                return True
            # 冲四类型2: 011112
            pattern_rush4_b = '0' + piece*4 + opponent_piece
            if pattern_rush4_b in line:
                return True
                
            # 3.双活三：在同一方向或不同方向
            #    这里暂不检测同一方向的双活三（因为在同一方向上不太可能同时形成两个活三），
            #    但可以检测不同方向的双活三（即在两个不同方向上都形成活三）
            pattern_live_3 = '0' + piece*3 + '0'
            for dr2, dc2 in directions:
                if (dr2, dc2) == (dr, dc):
                    continue  # 同一方向上不检测双活三
                line2 = self._get_line_string(row, col, dr2, dc2) 
                if pattern_live_3 in line and pattern_live_3 in line2: #这里我们直接用两个线上的活三代替了相交的双活三，看似不合理，但其实在实际落子中，如果在两个不同方向上都形成了活三，应该会提前堵住其中一个活三，所以我们用两个线上的活三来近似表示双活三的威胁
                    return True
            
        return False
    
    def get_forced_moves(self) -> List[Tuple[int, int]]:
        """ 
        获取一个自己当前必须下的位置列表（即如果不下这个位置，对手下一步就能赢了）
        """
        forced_moves = []
        candidates = self.get_candidate(radius=2)
        for r, c in candidates:
            if self.board.board[r][c] == 0:  # 只考虑空位
                # 模拟对手在这个位置落子
                self.board.board[r][c] = self.opponent
                if self.board.check_win(self.opponent, [r, c]):
                    self.board.board[r][c] = 0  # 恢复
                    return [(r, c)]  # 这个位置是一个直接的必杀点，必须堵住
                if self._has_forced_threat(self.opponent, r, c):
                    forced_moves.append((r, c))
                self.board.board[r][c] = 0  # 恢复
        return forced_moves
    
    # The minimax algorithm with alpha-beta pruning to evaluate the best move for the AI.
    def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool,current_score = 0, weight = 0.5):
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

                if self._has_forced_threat(self.player, r, c):
                    self.board.board[r][c] = 0
                    return (r, c), float('inf')  # This move creates a forced threat, so we can consider it as a winning move
                
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
                
                if self._has_forced_threat(opponent, r, c):
                    self.board.board[r][c] = 0
                    return (r, c), float('-inf')  # Opponent creates a forced threat, so we consider it as a losing move
                
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
    
        

