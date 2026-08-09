import argparse
import json
import sys
from pathlib import Path

# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Training.config import (
    DEFAULT_DEPTH,
    DEFAULT_GENERATIONS,
    DEFAULT_NUM_GAMES,
    DEFAULT_POP_SIZE,
    DEFAULT_SEED,
    OUTPUT_DIR,
)
from Training.genetic import run_ga


def parse_args():
    parser = argparse.ArgumentParser(description="Run Gomoku GA tuning.")
    parser.add_argument("--pop-size", type=int, default=DEFAULT_POP_SIZE)
    parser.add_argument("--generations", type=int, default=DEFAULT_GENERATIONS)
    parser.add_argument("--num-games", type=int, default=DEFAULT_NUM_GAMES)
    parser.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR))
    parser.add_argument("--artifact-prefix", type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    artifact_prefix = args.artifact_prefix or f"depth_{args.depth}"

    best_chrom, fitness = run_ga(
        pop_size=args.pop_size,
        generations=args.generations,
        num_games=args.num_games,
        depth=args.depth,
        seed=args.seed,
        output_dir=args.output_dir,
        artifact_prefix=artifact_prefix,
    )

    output_dir = Path(args.output_dir)
    legacy_best_path = output_dir / f"best_chrom_depth_{args.depth}.json"
    with legacy_best_path.open("w") as f:
        json.dump(best_chrom, f, indent=2)

    print(f"Final best fitness: {fitness:.3f}")
    print(f"Best chromosome saved to {legacy_best_path}")


if __name__ == "__main__":
    main()

