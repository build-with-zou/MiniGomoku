import unittest
from unittest.mock import patch

from board import Board
from human import Human


class HumanTests(unittest.TestCase):
    @patch("builtins.input", side_effect=["a b", "1 1"])
    def test_invalid_then_valid_input(self, mock_input):
        human = Human(Board(5), 1)
        self.assertEqual(human.get_move(), (0, 0))

    @patch("builtins.input", side_effect=["1 1", "1 2"])
    def test_occupied_then_valid_input(self, mock_input):
        board = Board(5)
        board.place(2, (0, 0))
        human = Human(board, 1)
        self.assertEqual(human.get_move(), (0, 1))


if __name__ == "__main__":
    unittest.main()

