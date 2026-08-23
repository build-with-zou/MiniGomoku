import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from AI.neural_model import PolicyValueNet


class PolicyValueNetTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)

    def test_forward_shapes_and_value_range(self):
        model = PolicyValueNet(board_size=9, channels=16, value_hidden=16)
        state = torch.zeros((2, 3, 9, 9), dtype=torch.float32)

        policy_logits, value = model(state)

        self.assertEqual(policy_logits.shape, (2, 81))
        self.assertEqual(value.shape, (2, 1))
        self.assertTrue(torch.isfinite(policy_logits).all())
        self.assertTrue(torch.isfinite(value).all())
        self.assertTrue(torch.all(value >= -1.0))
        self.assertTrue(torch.all(value <= 1.0))

    def test_single_state_is_supported(self):
        model = PolicyValueNet(board_size=5, channels=8, value_hidden=8)
        state = torch.zeros((3, 5, 5), dtype=torch.float32)

        policy_logits, value = model(state)

        self.assertEqual(policy_logits.shape, (1, 25))
        self.assertEqual(value.shape, (1, 1))

    def test_legal_mask_is_applied_before_softmax(self):
        logits = torch.tensor([[1.0, 2.0, 3.0, 4.0]])
        legal_mask = torch.tensor([[1.0, 0.0, 1.0, 0.0]])

        masked = PolicyValueNet.mask_policy_logits(logits, legal_mask)
        probabilities = torch.softmax(masked, dim=-1)

        self.assertEqual(masked[0, 1].item(), -1e9)
        self.assertEqual(masked[0, 3].item(), -1e9)
        self.assertAlmostEqual(probabilities.sum().item(), 1.0, delta=1e-6)
        self.assertEqual(probabilities[0, 1].item(), 0.0)
        self.assertEqual(probabilities[0, 3].item(), 0.0)

    def test_predict_returns_a_probability_distribution(self):
        model = PolicyValueNet(board_size=3, channels=8, value_hidden=8)
        state = torch.zeros((1, 3, 3, 3), dtype=torch.float32)
        legal_mask = np.array(
            [1, 0, 1, 0, 1, 1, 1, 1, 1],
            dtype=np.float32,
        )

        policy, value = model.predict(state, legal_mask=legal_mask)

        self.assertEqual(policy.shape, (1, 9))
        self.assertEqual(value.shape, (1, 1))
        self.assertAlmostEqual(policy.sum().item(), 1.0, delta=1e-6)
        self.assertEqual(policy[0, 1].item(), 0.0)
        self.assertEqual(policy[0, 3].item(), 0.0)

    def test_checkpoint_roundtrip(self):
        model = PolicyValueNet(board_size=5, channels=8, value_hidden=8)
        model.eval()
        state = torch.randn((2, 3, 5, 5), dtype=torch.float32)
        expected_policy, expected_value = model(state)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "policy_value.pt"
            model.save_checkpoint(path, epoch=3)
            restored = PolicyValueNet.from_checkpoint(path)
            restored.eval()
            actual_policy, actual_value = restored(state)

        torch.testing.assert_close(actual_policy, expected_policy)
        torch.testing.assert_close(actual_value, expected_value)

    def test_invalid_state_shape_is_rejected(self):
        model = PolicyValueNet(board_size=9)

        with self.assertRaises(ValueError):
            model(torch.zeros((1, 2, 9, 9)))

        with self.assertRaises(ValueError):
            model(torch.zeros((1, 3, 8, 8)))


if __name__ == "__main__":
    unittest.main()
