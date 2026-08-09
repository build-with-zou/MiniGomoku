# file name : genetic.py
# content : Genetic algorithm for optimizing Gomoku AI parameters.

import copy
import csv
import json
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AI.pattern import validate_chromosome
from Training.arena import compute_fitness
from Training.config import (
    BOARD_SIZE,
    DEFAULT_CHROM,
    DEFAULT_SEED,
    GENE_BOUNDS,
    OUTPUT_DIR,
)

history = []  # Kept for backward compatibility; refreshed on every run.


def random_chromosome():
    """Generate a random chromosome within the specified gene bounds."""
    chrom = []
    for low, high in GENE_BOUNDS:
        if isinstance(low, int) and isinstance(high, int):
            chrom.append(random.randint(low, high))
        else:
            chrom.append(round(random.uniform(low, high), 6))
    return validate_chromosome(chrom)


def tournament_select(population, scores, k=3):
    best_idx = None
    for _ in range(k):
        idx = random.randrange(len(population))
        if best_idx is None or scores[idx] > scores[best_idx]:
            best_idx = idx
    return copy.deepcopy(population[best_idx])


def uniform_crossover(p1, p2):
    """Perform uniform crossover between two parent chromosomes."""
    c1 = copy.deepcopy(p1)
    c2 = copy.deepcopy(p2)
    for i in range(len(c1)):
        if random.random() < 0.5:
            c1[i], c2[i] = c2[i], c1[i]
    return c1, c2


def mutate(chromosome, mutation_rate=0.1, scale=0.1):
    """Mutate a chromosome while keeping every gene within bounds."""
    new_chrom = copy.deepcopy(chromosome)
    for i, (low, high) in enumerate(GENE_BOUNDS):
        if random.random() < mutation_rate:
            delta = (high - low) * scale * random.gauss(0, 1)
            new_val = max(low, min(high, new_chrom[i] + delta))
            if isinstance(low, int) and isinstance(high, int):
                new_chrom[i] = int(round(new_val))
            else:
                new_chrom[i] = round(new_val, 6)
    return validate_chromosome(new_chrom)


def run_ga(
    pop_size=20,
    generations=30,
    opponent_chrom=None,
    elite_ratio=0.1,
    mutation_rate=0.1,
    mutation_scale=0.1,
    num_games=6,
    depth=2,
    seed=DEFAULT_SEED,
    output_dir=OUTPUT_DIR,
    artifact_prefix="ga_run",
    board_size=BOARD_SIZE,
    verbose=True,
):
    """
    Run the genetic algorithm and save the run artifacts.
    Returns (best_chromosome, best_fitness).
    """
    global history
    history = []

    if seed is not None:
        random.seed(seed)

    if opponent_chrom is None:
        opponent_chrom = DEFAULT_CHROM[:]
    opponent_chrom = validate_chromosome(opponent_chrom)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    population = [random_chromosome() for _ in range(pop_size)]
    best_chrom = population[0][:]
    best_fitness = float("-inf")

    for gen in range(generations):
        if verbose:
            print(f"===== Generation {gen + 1}/{generations} =====")

        scores = [0.0] * pop_size
        worker_count = max(1, min(os.cpu_count() or 1, pop_size))
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            future_to_idx = {
                executor.submit(
                    compute_fitness,
                    population[i],
                    opponent_chrom,
                    num_games,
                    depth,
                    None if seed is None else seed + gen * 10_000 + i,
                    board_size,
                    False,
                    False,
                ): i
                for i in range(pop_size)
            }
            completed = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    scores[idx] = future.result()
                except Exception as exc:
                    if verbose:
                        print(f"Error evaluating chromosome {idx}: {exc}")
                    scores[idx] = 0.0
                completed += 1
                if verbose:
                    print(f"  Evaluated {completed}/{pop_size} individuals", end="\r")
            if verbose:
                print()

        current_best_idx = max(range(len(scores)), key=lambda i: scores[i])
        current_best_score = scores[current_best_idx]
        current_best_chrom = population[current_best_idx][:]

        if verbose:
            print(
                f"Gen {gen + 1}: best fitness = {current_best_score:.3f}, "
                f"chromosome = {current_best_chrom}"
            )

        if current_best_score > best_fitness:
            best_fitness = current_best_score
            best_chrom = current_best_chrom[:]
            if verbose:
                print(f"  --> New global best: {best_fitness:.3f}")

        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        elite_count = max(1, int(pop_size * elite_ratio))
        elites = [population[i][:] for i in sorted_indices[:elite_count]]

        new_pop = elites[:]
        while len(new_pop) < pop_size:
            p1 = tournament_select(population, scores, k=3)
            p2 = tournament_select(population, scores, k=3)
            c1, c2 = uniform_crossover(p1, p2)
            c1 = mutate(c1, mutation_rate, mutation_scale)
            c2 = mutate(c2, mutation_rate, mutation_scale)
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        population = new_pop

        avg_fitness = sum(scores) / len(scores) if scores else 0.0
        history.append(
            {
                "gen": gen + 1,
                "max": max(scores) if scores else 0.0,
                "min": min(scores) if scores else 0.0,
                "avg": avg_fitness,
                "best_idx": current_best_idx,
                "best_score": current_best_score,
            }
        )
        if verbose:
            print(
                f"Gen {gen + 1}: max={max(scores):.3f}, min={min(scores):.3f}, "
                f"avg={avg_fitness:.3f}\n"
            )

    history_path = output_dir / f"{artifact_prefix}_history.csv"
    with history_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["gen", "max", "min", "avg", "best_idx", "best_score"])
        for row in history:
            writer.writerow(
                [
                    row["gen"],
                    row["max"],
                    row["min"],
                    row["avg"],
                    row["best_idx"],
                    row["best_score"],
                ]
            )

    best_path = output_dir / f"{artifact_prefix}_best_chrom.json"
    with best_path.open("w") as f:
        json.dump(best_chrom, f, indent=2)

    summary = {
        "best_chrom": best_chrom,
        "best_fitness": best_fitness,
        "population_size": pop_size,
        "generations": generations,
        "elite_ratio": elite_ratio,
        "mutation_rate": mutation_rate,
        "mutation_scale": mutation_scale,
        "num_games": num_games,
        "depth": depth,
        "seed": seed,
        "board_size": board_size,
        "opponent_chrom": opponent_chrom,
        "history_file": str(history_path),
        "best_file": str(best_path),
    }
    summary_path = output_dir / f"{artifact_prefix}_summary.json"
    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    return best_chrom, best_fitness
