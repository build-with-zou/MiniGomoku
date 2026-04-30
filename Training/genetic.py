# file name : genetic.py
# content : Genetic algorithm for optimizing Gomoku AI parameters, including fitness evaluation and selection of best chromosomes

import sys
from pathlib import Path
import os
# add parent directory to sys.path to allow imports from AI and Training modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import random
import copy
from Training.config import GENE_BOUNDS, CHROM_LENGTH, DEFAULT_CHROM
from Training.arena import compute_fitness

history = []  # To store the history of generations for analysis
os.makedirs("training/output", exist_ok=True)  # Ensure output directory exists

def random_chromosome():
    """Generate a random chromosome within the specified gene bounds"""
    chrom = []
    for low, high in GENE_BOUNDS:
        if isinstance(low, int) and isinstance(high, int):
            chrom.append(random.randint(low, high))
        else:
            chrom.append(round(random.uniform(low, high), 3))
    return chrom

def tournament_select(population, scores, k=3):
    best_idx = None
    for _ in range(k):
        idx = random.randrange(len(population))
        if best_idx is None or scores[idx] > scores[best_idx]:
            best_idx = idx
    return copy.deepcopy(population[best_idx])

def uniform_crossover(p1, p2):
    """
    Perform uniform crossover between two parent chromosomes.
    Each gene has a 50% chance of being swapped between the parents.
    """
    c1 = copy.deepcopy(p1)
    c2 = copy.deepcopy(p2)
    for i in range(len(c1)):
        if random.random() < 0.5:
            c1[i], c2[i] = c2[i], c1[i]
    return c1, c2

def mutate(chromosome, mutation_rate=0.1, scale=0.1):
    """
    mutation_rate: probability of mutating each gene,usually a small value like 0.1 or 0.05
    scale: controls the magnitude of mutation, as a fraction of the gene's range
    """
    new_chrom = copy.deepcopy(chromosome)
    for i in range(len(new_chrom)):
        if random.random() < mutation_rate:
            low, high = GENE_BOUNDS[i]
            delta = (high - low) * scale * random.gauss(0, 1)
            new_val = new_chrom[i] + delta 
            new_val = max(low, min(high, new_val)) # Ensure the mutated gene stays within bounds
            # 保持整数/浮点格式
            if isinstance(low, int) and isinstance(high, int):
                new_chrom[i] = int(round(new_val))
            else:
                new_chrom[i] = round(new_val, 3)
    return new_chrom

# ----- The main loop -----
def run_ga(pop_size=20, generations=30, opponent_chrom=None,
           elite_ratio=0.1, mutation_rate=0.1, mutation_scale=0.1,
           num_games=6, depth=2):
    """
    The main loop:

    Parameters:
        pop_size: Population size, default is 20
        generations: Number of generations, default is 30
        opponent_chrom: Fixed opponent chromosome, if None, DEFAULT_CHROM is used
        elite_ratio: Elite retention ratio
        mutation_rate: Probability of mutating each gene
        mutation_scale: Mutation magnitude factor (as a fraction of the gene's range)
        num_games: Number of games played to compute fitness (start small, then increase)
        depth: Search depth (AI depth used for evaluation, shallow depth recommended for speed)

    Returns:
        (best_chromosome, best_fitness)
    """
    # 1. Ensure opponent chromosome is set
    if opponent_chrom is None:
        opponent_chrom = DEFAULT_CHROM[:]
    
    # 2. Initialize population with random chromosomes
    population = [random_chromosome() for _ in range(pop_size)]
    # Seed with default chromosome is optional; currently commented out

    best_chrom = None
    best_fitness = 0.0

    # 3. Main evolution loop
    for gen in range(generations):
        print(f"===== Generation {gen+1}/{generations} =====")
        scores = []
        for idx, chrom in enumerate(population):
            print(f"Evaluating chromosome {idx+1}/{pop_size}...")
            fitness = compute_fitness(chrom, opponent_chrom,
                                      num_games=num_games, depth=depth)
            scores.append(fitness)
            print(f"  Fitness = {fitness:.3f}")

        # 3.2 Find the best individual in this generation and update the global best
        current_best_idx = max(range(len(scores)), key=lambda i: scores[i])
        print(f"Gen {gen}: best fitness = {scores[current_best_idx]:.3f}, chromosome = {population[current_best_idx]}")
        if scores[current_best_idx] > best_fitness:
            best_fitness = scores[current_best_idx]
            best_chrom = population[current_best_idx][:]
            print(f"  --> New global best: {best_fitness:.3f}")

        # 3.3 Elite selection: keep the top elite_ratio% of the population
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        elite_count = max(1, int(pop_size * elite_ratio))
        elites = [population[i][:] for i in sorted_indices[:elite_count]]

        # 3.4 Generate new population through selection, crossover, and mutation
        new_pop = elites[:]  # First, add the elites to the new population
        while len(new_pop) < pop_size:
            # Select two parents using tournament selection
            p1 = tournament_select(population, scores, k=3)
            p2 = tournament_select(population, scores, k=3)
            # Perform uniform crossover to generate two children
            c1, c2 = uniform_crossover(p1, p2)
            # Mutate the children
            c1 = mutate(c1, mutation_rate, mutation_scale)
            c2 = mutate(c2, mutation_rate, mutation_scale)
            # Add the children to the new population
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        # Replace the old population with the new one
        population = new_pop

        # Print statistics
        avg_fitness = sum(scores) / len(scores)
        history.append([gen, max(scores), min(scores), avg_fitness])
        print(f"Gen {gen}: max={max(scores):.3f}, min={min(scores):.3f}, avg={avg_fitness:.3f}\n")
        
    with open("training/output/history.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["gen", "max", "min", "avg"])
        writer.writerows(history)
    return best_chrom, best_fitness