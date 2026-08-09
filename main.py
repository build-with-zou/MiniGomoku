# File name : main.py
# Content: Console entry point for Gomoku.

import json
import os

from AI.Heuristic_ai_depth import HeuristicAIDepth
from AI.MCTS_ai import MCTS_AI
from Training.config import BOARD_SIZE, OUTPUT_DIR
from board import Board
from human import Human


def prompt_int(prompt, default=None, min_value=None, max_value=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("Invalid input. Please enter an integer.")
            continue
        if min_value is not None and value < min_value:
            print(f"Please enter a number >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Please enter a number <= {max_value}.")
            continue
        return value


def prompt_choice(prompt, choices, default=None):
    allowed = {str(choice) for choice in choices}
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        if raw in allowed:
            return raw
        print(f"Invalid choice. Choose one of: {', '.join(sorted(allowed))}.")


def load_weights_from_path(depth):
    default_path = OUTPUT_DIR / f"best_chrom_depth_{depth}.json"
    filepath = input(f"Enter weights file path (default: {default_path}): ").strip()
    if not filepath:
        filepath = str(default_path)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f), filepath
    print(f"File not found: {filepath}, using default weights instead.")
    return None, filepath


def build_players(board):
    print("Do you want to play against the AI? (y/n):")
    cin = input().strip().lower()

    if cin == "test":
        depth1 = prompt_int("Choose AI depth for player 1 (1-4): ", default=3, min_value=1, max_value=4)
        depth2 = prompt_int("Choose AI depth for player 2 (1-4): ", default=3, min_value=1, max_value=4)
        return (
            HeuristicAIDepth(board, 1, depth=depth1),
            HeuristicAIDepth(board, 2, depth=depth2),
            None,
        )

    if cin != "y":
        return Human(board, 1), Human(board, 2), None

    human_player = prompt_choice("Do you want to be Player 1 or Player 2? (Enter 1 or 2): ", choices=["1", "2"], default="1")
    human_player = int(human_player)
    ai_player = 2 if human_player == 1 else 1

    print("Choose AI type:")
    print("  1: HeuristicAI (depth search)")
    print("  2: MCTS AI (Monte Carlo Tree Search)")
    ai_type = prompt_choice("Enter 1 or 2 (default 1): ", choices=["1", "2"], default="1")

    if ai_type == "1":
        depth = prompt_int("Choose an AI difficulty level (1-4, default 3): ", default=3, min_value=1, max_value=4)
        use_ga = input("Use GA optimized weights? (y/n): ").strip().lower() == "y"
        weights = None
        if use_ga:
            weights, _ = load_weights_from_path(depth)

        if ai_player == 1:
            return (
                HeuristicAIDepth(board, ai_player, depth=depth, weights=weights),
                Human(board, human_player),
                {"type": "heuristic", "depth": depth, "weights": weights},
            )
        return (
            Human(board, human_player),
            HeuristicAIDepth(board, ai_player, depth=depth, weights=weights),
            {"type": "heuristic", "depth": depth, "weights": weights},
        )

    times = prompt_int("Enter MCTS simulation times per move (default 1000): ", default=1000, min_value=1)
    if ai_player == 1:
        return (
            MCTS_AI(board, player=ai_player, times=times),
            Human(board, human_player),
            {"type": "mcts", "times": times},
        )
    return (
        Human(board, human_player),
        MCTS_AI(board, player=ai_player, times=times),
        {"type": "mcts", "times": times},
    )


def main():
    print("Welcome to Gomoku!")
    size = prompt_int(
        f"Enter board size (default {BOARD_SIZE}): ",
        default=BOARD_SIZE,
        min_value=5,
        max_value=25,
    )
    board = Board(size)
    player1, player2, _ = build_players(board)

    current_player = player1
    while True:
        board.print_board()
        print("-" * (board.size * 2 - 1))
        print(f"Player {current_player.player}'s turn.")

        move = current_player.get_move()
        if move is None:
            print(f"Player {current_player.player} has no valid moves. Game ends in a draw.")
            for player in (player1, player2):
                if hasattr(player, "on_game_end"):
                    player.on_game_end(0)
            break

        if not board.apply_move(current_player.player, move):
            print("Invalid move, try again.")
            continue

        row, col = move
        print(f"Player {current_player.player} placed a piece at ({row + 1}, {col + 1}).")

        for player in (player1, player2):
            if hasattr(player, "observe_move"):
                player.observe_move(current_player.player, move)

        if board.check_win(current_player.player, move):
            board.print_board()
            print(f"Player {current_player.player} wins!")
            for player in (player1, player2):
                if hasattr(player, "on_game_end"):
                    player.on_game_end(current_player.player)
            break

        if board.is_full():
            board.print_board()
            print("It's a draw!")
            for player in (player1, player2):
                if hasattr(player, "on_game_end"):
                    player.on_game_end(0)
            break

        current_player = player2 if current_player == player1 else player1


if __name__ == "__main__":
    main()
