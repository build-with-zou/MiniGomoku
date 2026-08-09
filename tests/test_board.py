import unittest

from board import Board


class BoardTests(unittest.TestCase):
    def test_place_undo_and_clone(self):
        board = Board(5)
        self.assertTrue(board.place(1, (0, 0)))
        self.assertFalse(board.place(2, (0, 0)))
        self.assertEqual(board.last_move, (0, 0))
        self.assertTrue(board.undo_move())
        self.assertTrue(board.is_empty())

        board.place(1, (1, 1))
        clone = board.clone()
        self.assertTrue(clone.place(2, (0, 0)))
        self.assertEqual(board.board[0][0], 0)

    def test_win_detection(self):
        board = Board(5)
        for col in range(5):
            board.place(1, (0, col))
        self.assertTrue(board.check_win(1, (0, 4)))

        board = Board(5)
        for row in range(5):
            board.place(2, (row, 0))
        self.assertTrue(board.check_win(2, (4, 0)))

        board = Board(5)
        for i in range(5):
            board.place(1, (i, i))
        self.assertTrue(board.check_win(1, (4, 4)))

        board = Board(5)
        for i in range(5):
            board.place(2, (i, 4 - i))
        self.assertTrue(board.check_win(2, (4, 0)))


if __name__ == "__main__":
    unittest.main()

