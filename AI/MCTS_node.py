# File name: MCTS_node.py
# Content: MCTS node for Gomoku search.


class MCTSNode:
    def __init__(
        self,
        parent=None,
        pos=None,
        player=None,
        player_to_move=None,
        state_key=None,
        prior=0.0,
    ):
        self.parent = parent
        self.children = {}
        self.value = 0.0
        self.visits = 0
        self.untried_moves = []
        self.action = pos
        self.pos = pos
        self.player = player
        self.player_to_move = player_to_move if player_to_move is not None else (3 - player if player in (1, 2) else None)
        self.state_key = state_key
        self.prior = prior
        self.depth = 0 if parent is None else parent.depth + 1

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

