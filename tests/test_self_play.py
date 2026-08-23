import unittest
import argparse

import numpy as np

from Training.self_play import (
    build_parser,
    generate_dataset,
    play_teacher_game,
    resolve_teacher_arguments,
)


class SelfPlayDataTests(unittest.TestCase):
    def test_legacy_teacher_argument_is_supported(self):
        args = build_parser().parse_args(
            ["--teacher", "heuristic-depth2"]
        )
        self.assertEqual(resolve_teacher_arguments(args), ("heuristic", 2))

    def test_new_mixed_teacher_arguments_are_supported(self):
        args = build_parser().parse_args(
            ["--teacher-mode", "mixed", "--depth", "2"]
        )
        self.assertEqual(resolve_teacher_arguments(args), ("mixed", 2))

    def test_mixed_game_records_both_teacher_types(self):
        records, winner = play_teacher_game(
            size=9,
            depth=2,
            seed=42,
            teacher_mode="mixed",
            mcts_times=5,
        )

        self.assertIn(winner, (0, 1, 2))
        self.assertGreater(len(records), 0)
        self.assertEqual(
            {record["teacher"] for record in records},
            {"HeuristicAIDepth", "MCTS_AI"},
        )
        for record in records:
            self.assertEqual(record["state"].shape, (3, 9, 9))
            self.assertEqual(record["policy"].shape, (81,))
            self.assertAlmostEqual(float(record["policy"].sum()), 1.0)
            self.assertIn(record["value"], (-1.0, 0.0, 1.0))

    def test_mixed_dataset_contains_teacher_ids(self):
        states, policies, values, winners, teacher_ids = generate_dataset(
            games=2,
            size=9,
            depth=2,
            seed=42,
            teacher_mode="mixed",
            mcts_times=5,
            return_teacher_ids=True,
            verbose=False,
        )

        self.assertEqual(len(states), len(policies))
        self.assertEqual(len(states), len(values))
        self.assertEqual(len(states), len(teacher_ids))
        self.assertEqual(set(np.unique(teacher_ids).tolist()), {0, 1})
        self.assertEqual(sum(winners.values()), 2)


if __name__ == "__main__":
    unittest.main()
