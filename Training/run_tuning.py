import sys
from pathlib import Path

# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import os
from Training.genetic import run_ga
from Training.config import DEFAULT_CHROM

if __name__ == "__main__":
    best_chrom, fitness = run_ga(pop_size=12, generations=10, num_games=6, depth=3)
    print(f"Final best fitness: {fitness:.3f}")
    os.makedirs("training/output", exist_ok=True)
    with open("training/output/best_chrom_depth_3.json", "w") as f:
        json.dump(best_chrom, f)
    print("Best chromosome saved.")