# File name: pattern.py
# Content: Shared pattern definitions, weights, and validation helpers for Gomoku.

from copy import deepcopy
from typing import Sequence

_SWAP_PLAYER_TRANSLATION = str.maketrans("12", "21")

# Pattern dictionaries are the single source of truth for all heuristic players.
PLAYER_ONE_PATTERNS = {
    "0110": "活二",
    "01110": "活三",
    "011110": "活四",
    "01010": "跳二",
    "011010": "跳三",
    "010110": "跳三",
    "2110": "眠二",
    "0112": "眠二",
    "21110": "眠三",
    "01112": "眠三",
    "211110": "眠四",
    "011112": "眠四",
    "11111": "五",
}

PLAYER_ONE_OPPONENT_PATTERNS = {
    "0220": "活二",
    "02220": "活三",
    "022220": "活四",
    "02020": "跳二",
    "022020": "跳三",
    "020220": "跳三",
    "1220": "眠二",
    "0221": "眠二",
    "12220": "眠三",
    "02221": "眠三",
    "122220": "眠四",
    "022221": "眠四",
    "22222": "五",
}


def _swap_player_marks(patterns):
    return {pattern.translate(_SWAP_PLAYER_TRANSLATION): feature for pattern, feature in patterns.items()}


PATTERN_LIBRARY = {
    1: {
        "self": PLAYER_ONE_PATTERNS,
        "opponent": PLAYER_ONE_OPPONENT_PATTERNS,
    },
    2: {
        "self": _swap_player_marks(PLAYER_ONE_PATTERNS),
        "opponent": _swap_player_marks(PLAYER_ONE_OPPONENT_PATTERNS),
    },
}

# Pattern scores are the default heuristic weights used by the existing AI.
DEFAULT_PATTERN_SCORE = {
    "potential": {
        "活二": 10,
        "跳二": 5,
        "活三": 1000,
        "跳三": 500,
        "活四": 10000,
        "五": 10000,
    },
    "sleep": {
        "眠二": 5,
        "眠三": 50,
        "眠四": 2000,
    },
}

# Chromosome layout used by the genetic algorithm.
GENE_LABELS = (
    "活二",
    "跳二",
    "活三",
    "跳三",
    "活四",
    "五",
    "眠二",
    "眠三",
    "眠四",
    "defense_weight",
)

DEFAULT_GENE_BOUNDS = [
    (1, 50),        # 活二
    (1, 30),        # 跳二
    (100, 2000),    # 活三
    (50, 1000),     # 跳三
    (5000, 50000),  # 活四
    (10000, 1000000),  # 五
    (1, 30),        # 眠二
    (10, 200),      # 眠三
    (500, 10000),   # 眠四
    (0.1, 1.5),     # defense weight
]

DEFAULT_CHROMOSOME = [10, 5, 1000, 500, 10000, 10000, 5, 50, 2000, 0.5]


def get_pattern_map(player: int):
    """Return the canonical pattern dictionary for a player color."""
    return PATTERN_LIBRARY[player]["self"]


def get_opponent_pattern_map(player: int):
    """Return the canonical pattern dictionary for the opponent of a player color."""
    return PATTERN_LIBRARY[player]["opponent"]


def get_pattern_pair(player: int):
    """Return both the player's and opponent's pattern dictionaries."""
    return get_pattern_map(player), get_opponent_pattern_map(player)


def validate_chromosome(chromosome: Sequence[float | int], bounds=None):
    """
    Validate and normalize a chromosome.

    Returns a list with ints for integer ranges and floats for float ranges.
    Raises ValueError if length or bounds are invalid.
    """
    if bounds is None:
        bounds = DEFAULT_GENE_BOUNDS

    if chromosome is None:
        raise ValueError("chromosome cannot be None")

    if len(chromosome) != len(bounds):
        raise ValueError(
            f"chromosome length must be {len(bounds)}, got {len(chromosome)}"
        )

    normalized = []
    for idx, (value, (low, high)) in enumerate(zip(chromosome, bounds)):
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"gene {idx} is not numeric: {value!r}") from exc

        if not (low <= numeric <= high):
            raise ValueError(
                f"gene {idx}={numeric} is out of bounds [{low}, {high}]"
            )

        if isinstance(low, int) and isinstance(high, int):
            if not float(numeric).is_integer():
                raise ValueError(f"gene {idx} must be an integer value, got {numeric!r}")
            normalized.append(int(round(numeric)))
        else:
            normalized.append(round(numeric, 6))

    return normalized


class Pattern:
    """Container for shared patterns and heuristic weights."""

    def __init__(self, player, weights=None):
        self.player = player
        self.opponent = 2 if player == 1 else 1
        self.defensive_weight = DEFAULT_CHROMOSOME[9]
        self.pattern = get_pattern_map(player)
        self.opponent_pattern = get_opponent_pattern_map(player)
        self.pattern_score = deepcopy(DEFAULT_PATTERN_SCORE)
        self.chromosome = DEFAULT_CHROMOSOME[:]

        if weights is not None:
            self.set_weights(weights)

    def get_pattern(self, player=None):
        """Return the pattern dictionary for the given player color."""
        if player is None:
            player = self.player
        return get_pattern_map(player)

    def get_opponent_pattern(self, player=None):
        """Return the opponent pattern dictionary for the given player color."""
        if player is None:
            player = self.player
        return get_opponent_pattern_map(player)

    def set_weights(self, chromosome):
        """
        Set the heuristic weights from a chromosome.
        Layout:
            0-5: potential pattern scores
            6-8: sleep pattern scores
            9: defensive weight
        """
        validated = validate_chromosome(chromosome)
        self.chromosome = validated
        self.pattern_score = {
            "potential": {
                "活二": validated[0],
                "跳二": validated[1],
                "活三": validated[2],
                "跳三": validated[3],
                "活四": validated[4],
                "五": validated[5],
            },
            "sleep": {
                "眠二": validated[6],
                "眠三": validated[7],
                "眠四": validated[8],
            },
        }
        self.defensive_weight = validated[9]
