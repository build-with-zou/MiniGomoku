import unittest

import numpy as np

from AI.encoder import Code, encode_board, encoder, get_code, legal_move_mask
from board import Board


class EncoderTests(unittest.TestCase):
    def test_to_numpy_black_perspective(self):
        board = Board(3)
        board.place(1, (0, 0))
        board.place(2, (1, 1))

        encoded = encoder(board)
        self.assertIsInstance(encoded, Code)

        state = encoded.to_numpy()
        self.assertEqual(state.shape, (3, 3, 3))
        self.assertEqual(state.dtype, np.float32)
        self.assertEqual(state[0, 0, 0], 1.0)
        self.assertEqual(state[1, 1, 1], 1.0)
        self.assertTrue(np.all(state[2] == 1.0))

        direct = encode_board(board)
        alias = get_code(board)
        np.testing.assert_array_equal(direct, state)
        np.testing.assert_array_equal(alias, state)

    def test_to_numpy_white_perspective(self):
        board = Board(3)
        board.place(1, (0, 0))

        state = encoder(board).to_numpy()
        self.assertEqual(state.shape, (3, 3, 3))
        self.assertTrue(np.all(state[0] == 0.0))
        self.assertEqual(state[1, 0, 0], 1.0)
        self.assertTrue(np.all(state[2] == 0.0))

    def test_move_index_roundtrip_and_bounds(self):
        code = encoder(Board(5))

        self.assertEqual(code.move_to_index((1, 2)), 7)
        self.assertEqual(code.index_to_move(7), (1, 2))

        for bad_move in [(-1, 0), (0, -1), (5, 0), (0, 5), "12", (1,), (1, 2, 3)]:
            with self.assertRaises(ValueError):
                code.move_to_index(bad_move)

        for bad_index in [-1, 25, 25.0, "3"]:
            with self.assertRaises(ValueError):
                code.index_to_move(bad_index)

    def test_legal_move_mask(self):
        board = Board(3)
        board.place(1, (0, 0))
        board.place(2, (1, 1))

        expected_2d = np.array(
            [
                [0, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
            ],
            dtype=np.float32,
        )

        mask_2d = legal_move_mask(board, flatten=False)
        mask_1d = legal_move_mask(board)
        np.testing.assert_array_equal(mask_2d, expected_2d)
        np.testing.assert_array_equal(mask_1d, expected_2d.reshape(-1))

    def test_legal_move_mask_full_board(self):
        board = Board(2)
        board.place(1, (0, 0))
        board.place(2, (0, 1))
        board.place(1, (1, 0))
        board.place(2, (1, 1))

        mask = legal_move_mask(board)
        np.testing.assert_array_equal(mask, np.zeros(4, dtype=np.float32))


if __name__ == "__main__":
    unittest.main()
