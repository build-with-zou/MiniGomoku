# File name: config.py
# Content: Shared training configuration for Gomoku AI tuning.

from pathlib import Path

from AI.pattern import DEFAULT_CHROMOSOME, DEFAULT_GENE_BOUNDS

# Game / training defaults
BOARD_SIZE = 15
DEFAULT_DEPTH = 3
DEFAULT_POP_SIZE = 12
DEFAULT_GENERATIONS = 10
DEFAULT_NUM_GAMES = 6
DEFAULT_SEED = 42

# Genetic algorithm chromosome layout
GENE_BOUNDS = DEFAULT_GENE_BOUNDS
CHROM_LENGTH = len(GENE_BOUNDS)
DEFAULT_CHROM = DEFAULT_CHROMOSOME[:]

# Output location for all training artifacts
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

