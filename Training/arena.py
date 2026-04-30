# file name : arena.py
# content : Arena for training Gomoku AI, where two AIs can compete against each other and collect data for training
import sys
from pathlib import Path

# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from board import Board
from AI.Heuristic_ai_depth import HeuristicAIDepth

def play_game(ai1, ai2, size=15):
    board = Board(size)
    ai1.board = board
    ai2.board = board
    current_player = 1
    while True:
        ai = ai1 if current_player == 1 else ai2
        move = ai.get_move()
        if move is None:
            return 0
        board.place(current_player, list(move))
        if board.check_win(current_player, move):
            return current_player
        if board.is_full():
            return 0
        current_player = 3 - current_player

def compute_fitness(chromosome, opponent_chromosome=None, num_games=10, depth=2):
    if opponent_chromosome is None:
        from Training.config import DEFAULT_CHROM
        opponent_chromosome = DEFAULT_CHROM

    wins = 0
    for i in range(num_games):
        print(f"    Game {i+1}/{num_games}...", end=" ")
        board = Board(15)
        if i % 2 == 0:      # 偶数局：测试方执先手
            ai1 = HeuristicAIDepth(board, player=1, depth=depth, weights=chromosome)
            ai2 = HeuristicAIDepth(board, player=2, depth=depth, weights=opponent_chromosome)
        else:               # 奇数局：测试方执后手
            ai1 = HeuristicAIDepth(board, player=1, depth=depth, weights=opponent_chromosome)
            ai2 = HeuristicAIDepth(board, player=2, depth=depth, weights=chromosome)

        winner = play_game(ai1, ai2)
        if (i % 2 == 0 and winner == 1) or (i % 2 == 1 and winner == 2):
            wins += 1
            print("test win")
        else:
            print("test lose")
    return wins / num_games

# if __name__ == "__main__":
#     # Test the fitness function with default chromosome against itself
#     from config import DEFAULT_CHROM
#     fitness = compute_fitness(DEFAULT_CHROM, DEFAULT_CHROM, num_games=4, depth=2)
#     print(f"Default vs default winrate: {fitness:.2f}")


if __name__ == "__main__":
    from config import DEFAULT_CHROM

    # 构造一个极弱染色体（活三只有1分，眠三只有1分）
    weak = [1, 1, 1, 1, 1, 10000, 1, 1, 1, 0.5]

    print("Default self-play:", compute_fitness(DEFAULT_CHROM, DEFAULT_CHROM, num_games=10, depth=2))
    print("Weak vs Default:", compute_fitness(weak, DEFAULT_CHROM, num_games=10, depth=2))