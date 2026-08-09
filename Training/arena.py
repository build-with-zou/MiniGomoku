# file name : arena.py
# content : Arena for training Gomoku AI, where two AIs can compete against each other.

import random
import sys
from pathlib import Path

# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from board import Board
from AI.Heuristic_ai_depth import HeuristicAIDepth
from AI.pattern import validate_chromosome
from Training.config import BOARD_SIZE, DEFAULT_CHROM


def _bind_player(player_obj, board):
    if hasattr(player_obj, "set_board"):
        player_obj.set_board(board)
    else:
        player_obj.board = board
    if hasattr(player_obj, "reset"):
        player_obj.reset()


def play_game(ai1, ai2, size=BOARD_SIZE, seed=None, verbose=False):
    if seed is not None:
        random.seed(seed)

    board = Board(size)
    _bind_player(ai1, board)
    _bind_player(ai2, board)

    current_player = 1
    while True:
        ai = ai1 if current_player == 1 else ai2
        move = ai.get_move()
        if move is None:
            if hasattr(ai1, "on_game_end"):
                ai1.on_game_end(0)
            if hasattr(ai2, "on_game_end"):
                ai2.on_game_end(0)
            return 0

        if not board.apply_move(current_player, move):
            loser = current_player
            winner = 3 - loser
            if hasattr(ai1, "on_game_end"):
                ai1.on_game_end(winner)
            if hasattr(ai2, "on_game_end"):
                ai2.on_game_end(winner)
            return winner

        for player_obj in (ai1, ai2):
            if hasattr(player_obj, "observe_move"):
                player_obj.observe_move(current_player, move)

        if verbose:
            print(f"Player {current_player} -> ({move[0] + 1}, {move[1] + 1})")

        if board.check_win(current_player, move):
            if hasattr(ai1, "on_game_end"):
                ai1.on_game_end(current_player)
            if hasattr(ai2, "on_game_end"):
                ai2.on_game_end(current_player)
            return current_player

        if board.is_full():
            if hasattr(ai1, "on_game_end"):
                ai1.on_game_end(0)
            if hasattr(ai2, "on_game_end"):
                ai2.on_game_end(0)
            return 0

        current_player = 3 - current_player


def compute_fitness(
    chromosome,
    opponent_chromosome=None,
    num_games=10,
    depth=2,
    seed=None,
    size=BOARD_SIZE,
    return_details=False,
    verbose=True,
):
    if opponent_chromosome is None:
        opponent_chromosome = DEFAULT_CHROM

    chromosome = validate_chromosome(chromosome)
    opponent_chromosome = validate_chromosome(opponent_chromosome)

    wins = 0
    losses = 0
    draws = 0

    for i in range(num_games):
        if verbose:
            print(f"    Game {i + 1}/{num_games}...", end=" ")
        game_seed = None if seed is None else seed + i
        if i % 2 == 0:
            ai1 = HeuristicAIDepth(Board(size), player=1, depth=depth, weights=chromosome)
            ai2 = HeuristicAIDepth(Board(size), player=2, depth=depth, weights=opponent_chromosome)
            test_side = 1
        else:
            ai1 = HeuristicAIDepth(Board(size), player=1, depth=depth, weights=opponent_chromosome)
            ai2 = HeuristicAIDepth(Board(size), player=2, depth=depth, weights=chromosome)
            test_side = 2

        winner = play_game(ai1, ai2, size=size, seed=game_seed)
        if (test_side == 1 and winner == 1) or (test_side == 2 and winner == 2):
            wins += 1
            outcome = "test win"
        elif winner == 0:
            draws += 1
            outcome = "draw"
        else:
            losses += 1
            outcome = "test lose"

        if verbose:
            print(outcome)

    fitness = wins / num_games if num_games else 0.0
    details = {
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "games": num_games,
        "fitness": fitness,
    }
    if return_details:
        return fitness, details
    return fitness


if __name__ == "__main__":
    weak = [1, 1, 1, 1, 1, 10000, 1, 1, 1, 0.5]
    print("Default self-play:", compute_fitness(DEFAULT_CHROM, DEFAULT_CHROM, num_games=4, depth=2))
    print("Weak vs Default:", compute_fitness(weak, DEFAULT_CHROM, num_games=4, depth=2))

