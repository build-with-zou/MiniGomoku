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
        # change the order of players to ensure fairness in evaluation
        if i % 2 == 0:
            chrom1, chrom2 = chromosome, opponent_chromosome
            player1_id = 1
            player2_id = 2
        else:
            chrom1, chrom2 = opponent_chromosome, chromosome
            player1_id = 2
            player2_id = 1
        board = Board(15)
        ai1 = HeuristicAIDepth(board, player1_id, depth, weights=chrom1)
        ai2 = HeuristicAIDepth(board, player2_id, depth, weights=chrom2)
        winner = play_game(ai1, ai2)
        if (i % 2 == 0 and winner == 1) or (i % 2 == 1 and winner == 2):
            wins += 1
    return wins / num_games

if __name__ == "__main__":
    # Test the fitness function with default chromosome against itself
    from config import DEFAULT_CHROM
    fitness = compute_fitness(DEFAULT_CHROM, DEFAULT_CHROM, num_games=4, depth=2)
    print(f"Default vs default winrate: {fitness:.2f}")