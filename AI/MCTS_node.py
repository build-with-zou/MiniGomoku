# File name: MCTS_node.py
# Content: MCTS node for later use in MCTS AI

class MCTSNode:
    def __init__(self, parent=None, pos=None, player=None):
        self.parent = parent
        self.children = {}          # 键：落子位置 (row, col)，值：MCTSNode
        self.value = 0.0            # 累计价值（赢=1，输=-1，平=0）
        self.visits = 0             # 访问次数
        self.untried_moves = []     # 尚未扩展的合法走法列表，元素为 (row, col)
        self.pos = pos              # 导致该节点的走法坐标
        self.player = player        # 走该步棋的玩家（1 或 2）

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0