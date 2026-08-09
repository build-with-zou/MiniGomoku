import unittest

from AI.pattern import (
    DEFAULT_CHROMOSOME,
    get_opponent_pattern_map,
    get_pattern_map,
    validate_chromosome,
)


class PatternTests(unittest.TestCase):
    def test_pattern_mirroring(self):
        self.assertEqual(get_pattern_map(1)["0110"], "活二")
        self.assertEqual(get_opponent_pattern_map(1)["0220"], "活二")
        self.assertEqual(get_pattern_map(2)["0220"], "活二")
        self.assertEqual(get_opponent_pattern_map(2)["0110"], "活二")

    def test_validate_chromosome(self):
        chrom = validate_chromosome(DEFAULT_CHROMOSOME)
        self.assertEqual(chrom, DEFAULT_CHROMOSOME)
        with self.assertRaises(ValueError):
            validate_chromosome(DEFAULT_CHROMOSOME[:-1])


if __name__ == "__main__":
    unittest.main()

