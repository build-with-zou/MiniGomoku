"""Generate bootstrap training data from one or more existing AIs.

This is teacher-data generation, not neural-network self-play yet.
Each position in a game becomes one training sample:

    state   -> encoded board from the current player's perspective
    policy  -> one-hot vector for the teacher's selected move
    value   -> final game result from that position's perspective
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

# Allow ``python Training/self_play.py`` to import project modules.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AI.Heuristic_ai_depth import HeuristicAIDepth
from AI.encoder import encode_board
from AI.MCTS_ai import MCTS_AI
from board import Board


TEACHER_IDS = {
    "HeuristicAIDepth": 0,
    "MCTS_AI": 1,
}


def _build_teachers(
    board: Board,
    *,
    depth: int,
    weights,
    teacher_mode: str,
    mcts_times: int,
    game_index: int,
):
    """Build the two players used for one game.

    In mixed mode, the players swap colors on alternate games. This avoids
    making one teacher permanently responsible for the first move.
    """
    valid_modes = {"heuristic", "mcts", "mixed"}
    if teacher_mode not in valid_modes:
        raise ValueError(
            f"teacher_mode must be one of {sorted(valid_modes)}, got {teacher_mode!r}"
        )
    if mcts_times <= 0:
        raise ValueError("mcts_times must be greater than zero")

    heuristic = lambda player: HeuristicAIDepth(
        board,
        player=player,
        depth=depth,
        weights=weights,
    )
    mcts = lambda player: MCTS_AI(
        board,
        player=player,
        times=mcts_times,
    )

    if teacher_mode == "heuristic":
        return {
            1: heuristic(1),
            2: heuristic(2),
        }, {
            1: "HeuristicAIDepth",
            2: "HeuristicAIDepth",
        }

    if teacher_mode == "mcts":
        return {
            1: mcts(1),
            2: mcts(2),
        }, {
            1: "MCTS_AI",
            2: "MCTS_AI",
        }

    # Mixed mode: alternate which teacher gets player 1.
    if game_index % 2 == 0:
        return {
            1: heuristic(1),
            2: mcts(2),
        }, {
            1: "HeuristicAIDepth",
            2: "MCTS_AI",
        }
    return {
        1: mcts(1),
        2: heuristic(2),
    }, {
        1: "MCTS_AI",
        2: "HeuristicAIDepth",
    }


def play_teacher_game(
    size: int,
    depth: int,
    seed: int | None = None,
    weights=None,
    teacher_mode: str = "heuristic",
    mcts_times: int = 100,
    game_index: int = 0,
    verbose: bool = False,
):
    """Play one game and return raw training samples plus the winner."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    board = Board(size)
    players, teacher_names = _build_teachers(
        board,
        depth=depth,
        weights=weights,
        teacher_mode=teacher_mode,
        mcts_times=mcts_times,
        game_index=game_index,
    )
    records = []
    current_player = 1

    while True:
        # Capture the state before the move. The encoder uses board.cnt_player,
        # which should match current_player because Board.apply_move toggles it.
        state = encode_board(board)
        if board.cnt_player != current_player:
            raise RuntimeError(
                "board.cnt_player and current_player disagree: "
                f"{board.cnt_player} != {current_player}"
            )

        move = players[current_player].get_move()
        if move is None:
            winner = 0
            break

        row, col = move
        if not board.is_legal_move(move):
            raise RuntimeError(
                f"teacher returned illegal move {move} on board:\n{board.board}"
            )

        policy = np.zeros(size * size, dtype=np.float32)
        policy[row * size + col] = 1.0
        records.append(
            {
                "state": state,
                "policy": policy,
                "player": current_player,
                "teacher": teacher_names[current_player],
            }
        )

        if not board.apply_move(current_player, move):
            raise RuntimeError(f"Board rejected legal teacher move {move}")

        if verbose:
            print(
                f"player={current_player} move=({row}, {col}) "
                f"ply={board.move_count}"
            )

        if board.check_win(current_player, move):
            winner = current_player
            break
        if board.is_full():
            winner = 0
            break

        current_player = 3 - current_player

    # Value is always relative to the player who was about to move in the
    # recorded state, not relative to black globally.
    for record in records:
        if winner == 0:
            record["value"] = 0.0
        elif winner == record["player"]:
            record["value"] = 1.0
        else:
            record["value"] = -1.0

    return records, winner


def generate_dataset(
    games: int,
    size: int,
    depth: int,
    seed: int | None = 42,
    weights=None,
    teacher_mode: str = "heuristic",
    mcts_times: int = 100,
    return_teacher_ids: bool = False,
    verbose: bool = True,
):
    """Generate and stack samples from multiple teacher games.

    ``return_teacher_ids=False`` keeps the original four-value return shape
    for callers that only need states, policies, values, and winners.
    """
    if games <= 0:
        raise ValueError("games must be greater than zero")
    if size < 5:
        raise ValueError("size must be at least 5 for Gomoku")
    if depth <= 0:
        raise ValueError("depth must be greater than zero")
    if mcts_times <= 0:
        raise ValueError("mcts_times must be greater than zero")

    all_records = []
    winners = {0: 0, 1: 0, 2: 0}

    for game_index in range(games):
        game_seed = None if seed is None else seed + game_index
        records, winner = play_teacher_game(
            size=size,
            depth=depth,
            seed=game_seed,
            weights=weights,
            teacher_mode=teacher_mode,
            mcts_times=mcts_times,
            game_index=game_index,
            verbose=False,
        )
        all_records.extend(records)
        winners[winner] += 1
        if verbose:
            print(
                f"game {game_index + 1}/{games}: "
                f"winner={winner} samples={len(records)}"
            )

    if not all_records:
        raise RuntimeError("no training samples were generated")

    states = np.stack([record["state"] for record in all_records]).astype(
        np.float32,
        copy=False,
    )
    policies = np.stack([record["policy"] for record in all_records]).astype(
        np.float32,
        copy=False,
    )
    values = np.asarray(
        [record["value"] for record in all_records],
        dtype=np.float32,
    )

    teacher_ids = np.asarray(
        [TEACHER_IDS[record["teacher"]] for record in all_records],
        dtype=np.int64,
    )

    if return_teacher_ids:
        return states, policies, values, winners, teacher_ids
    return states, policies, values, winners


def save_dataset(
    output_path: str | Path,
    states: np.ndarray,
    policies: np.ndarray,
    values: np.ndarray,
    *,
    size: int,
    games: int,
    depth: int,
    seed: int | None,
    winners: dict[int, int],
    teacher_mode: str = "heuristic",
    mcts_times: int = 100,
    teacher_ids: np.ndarray | None = None,
) -> None:
    """Save samples and metadata in one compressed NumPy archive."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "board_size": size,
        "games": games,
        "teacher_mode": teacher_mode,
        "teacher_depth": depth,
        "mcts_times": mcts_times,
        "teacher_id_map": TEACHER_IDS,
        "seed": seed,
        "winners": {str(key): value for key, value in winners.items()},
        "state_shape": list(states.shape[1:]),
        "policy_shape": list(policies.shape[1:]),
    }
    arrays = {
        "states": states,
        "policies": policies,
        "values": values,
        "metadata": json.dumps(metadata, ensure_ascii=True),
    }
    if teacher_ids is not None:
        arrays["teacher_ids"] = teacher_ids
    np.savez_compressed(output_path, **arrays)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate bootstrap policy/value data with existing AI teachers."
    )
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--size", type=int, default=9)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument(
        "--teacher-mode",
        choices=("heuristic", "mcts", "mixed"),
        default="heuristic",
        help="teacher pairing mode; mixed swaps heuristic/MCTS colors per game",
    )
    parser.add_argument(
        "--teacher",
        default=None,
        help=(
            "legacy alias: heuristic-depth2, heuristic, mcts, or mixed; "
            "prefer --teacher-mode and --depth"
        ),
    )
    parser.add_argument(
        "--mcts-times",
        type=int,
        default=100,
        help="MCTS simulations per move when mcts or mixed mode is used",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/selfplay/bootstrap_9x9.npz"),
    )
    parser.add_argument("--quiet", action="store_true")
    return parser


def resolve_teacher_arguments(args: argparse.Namespace) -> tuple[str, int]:
    """Resolve new teacher options and the old ``--teacher`` alias."""
    if not args.teacher:
        return args.teacher_mode, args.depth

    token = args.teacher.strip().lower().replace("_", "-")
    if token in {"heuristic", "mcts", "mixed"}:
        return token, args.depth
    if token.startswith("heuristic-depth"):
        depth_text = token.removeprefix("heuristic-depth")
        try:
            depth = int(depth_text)
        except ValueError as exc:
            raise ValueError(
                "legacy --teacher must look like heuristic-depth2"
            ) from exc
        return "heuristic", depth
    if token.startswith("mcts-"):
        # ``--teacher mcts-100`` is accepted as a convenience alias. The
        # simulation count itself is still controlled by --mcts-times.
        return "mcts", args.depth

    raise ValueError(
        "unknown --teacher value; use heuristic-depth2, heuristic, mcts, "
        "or mixed"
    )


def main() -> None:
    args = build_parser().parse_args()
    try:
        teacher_mode, depth = resolve_teacher_arguments(args)
    except ValueError as exc:
        build_parser().error(str(exc))

    generated = generate_dataset(
        games=args.games,
        size=args.size,
        depth=depth,
        seed=args.seed,
        teacher_mode=teacher_mode,
        mcts_times=args.mcts_times,
        return_teacher_ids=True,
        verbose=not args.quiet,
    )

    # The current generator returns five values. Accept the older four-value
    # return shape too, so a partially updated local copy does not fail with
    # "too many/not enough values to unpack" at this call site.
    if len(generated) == 5:
        states, policies, values, winners, teacher_ids = generated
    elif len(generated) == 4:
        states, policies, values, winners = generated
        fallback_teacher_id = {
            "heuristic": TEACHER_IDS["HeuristicAIDepth"],
            "mcts": TEACHER_IDS["MCTS_AI"],
        }.get(teacher_mode, -1)
        teacher_ids = np.full(
            len(states),
            fallback_teacher_id,
            dtype=np.int64,
        )
    else:
        raise RuntimeError(
            "generate_dataset() must return 4 or 5 values, "
            f"got {len(generated)}"
        )

    save_dataset(
        args.out,
        states,
        policies,
        values,
        size=args.size,
        games=args.games,
        depth=depth,
        seed=args.seed,
        winners=winners,
        teacher_mode=teacher_mode,
        mcts_times=args.mcts_times,
        teacher_ids=teacher_ids,
    )

    print(f"saved: {args.out}")
    print(f"states: {states.shape} dtype={states.dtype}")
    print(f"policies: {policies.shape} dtype={policies.dtype}")
    print(f"values: {values.shape} unique={np.unique(values).tolist()}")
    print(
        "teacher_samples: "
        f"heuristic={int(np.sum(teacher_ids == TEACHER_IDS['HeuristicAIDepth']))} "
        f"mcts={int(np.sum(teacher_ids == TEACHER_IDS['MCTS_AI']))}"
    )
    print(f"winners: {winners}")


if __name__ == "__main__":
    main()
