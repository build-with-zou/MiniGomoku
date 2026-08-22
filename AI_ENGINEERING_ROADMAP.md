# MiniGomoku AI 工程化路线文档

更新时间：2026-08-22

本文档用于跟踪 MiniGomoku 从“规则搜索 AI”走向“可学习 AI”的工程路线。每个任务都使用 Markdown 任务列表表示：

- `[ ]` 表示未完成
- `[x]` 表示已完成

后续开发时，完成一个任务就把对应行从 `[ ]` 改成 `[x]`。

---

## 1. 总目标

当前项目已经具备传统游戏 AI 的基础：规则棋盘、启发式评估、alpha-beta 搜索、MCTS、遗传算法调权和基础测试。下一阶段的核心目标不是继续堆更多手写规则，而是加入一个可以从数据中学习的模型。

最终目标：

```text
规则棋盘 Board
  -> 局面编码 Encoder
  -> 策略价值网络 PolicyValueNet
  -> 神经网络引导的 MCTS
  -> 自我对弈生成数据
  -> 训练新模型
  -> 新旧模型评测
  -> 通过评测后替换最佳模型
```

这条路线接近 AlphaZero 的简化工程版本，适合当前 MiniGomoku 结构逐步演进。

---

## 2. 当前项目状态

### 2.1 已具备能力

- [x] `board.py` 是规则和棋盘状态的唯一来源
- [x] 支持合法落子：`Board.apply_move(player, pos)`
- [x] 支持撤销：`Board.undo_move(pos=None)`
- [x] 支持复制棋盘：`Board.clone()`
- [x] 支持局面 key：`Board.create_key()`
- [x] 支持胜负判断：`Board.check_win(player, pos)`
- [x] 已有统一玩家接口：`AI/base.py`
- [x] 已有启发式搜索 AI：`AI/Heuristic_ai_depth.py`
- [x] 已有随机 rollout MCTS：`AI/MCTS_ai.py`
- [x] MCTS 节点已有 `prior` 字段，方便接策略网络
- [x] 已有训练 arena：`Training/arena.py`
- [x] 已有遗传算法调参：`Training/genetic.py`
- [x] 已有基础测试目录：`tests/`
- [x] 当前基础测试通过：`python -m unittest discover -s tests`
- [x] 工作区已有初版 `requirements.txt`，包含 `numpy`、`torch`、`tqdm`
- [x] 已有三通道相对视角编码器：`AI/encoder.py`
- [x] 编码器可区分当前玩家棋子、对手棋子和当前行棋方颜色
- [x] 已有二维合法落子 mask：空位为 `1`，已占用位置为 `0`
- [x] 已有二维坐标与一维策略索引的转换公式

### 2.2 当前主要限制

- [ ] `encoder(board)` 仍然返回 `Code` 容器；如果希望更简洁，还可以进一步改成直接返回数组
- [ ] 没有策略价值神经网络
- [ ] 没有自我对弈数据格式
- [ ] 没有神经网络训练脚本
- [ ] MCTS 仍然依赖随机 rollout，没有使用网络 value
- [ ] MCTS 没有使用 policy prior
- [ ] 没有模型版本管理
- [ ] 没有新旧模型自动评测
- [ ] 没有 AlphaZero 式训练循环
- [ ] GUI 和 CLI 还不能选择神经网络 AI

---

## 3. 目标目录结构

建议逐步把项目扩展成下面结构：

```text
.
├── AI/
│   ├── base.py
│   ├── pattern.py
│   ├── Heuristic_ai.py
│   ├── Heuristic_ai_depth.py
│   ├── MCTS_ai.py
│   ├── MCTS_node.py
│   ├── encoder.py
│   ├── neural_model.py
│   └── NeuralMCTS_ai.py
├── Training/
│   ├── config.py
│   ├── arena.py
│   ├── genetic.py
│   ├── run_tuning.py
│   ├── self_play.py
│   ├── train_policy_value.py
│   ├── evaluate.py
│   └── az_loop.py
├── data/
│   └── selfplay/
├── models/
│   ├── best.pt
│   └── checkpoints/
├── tests/
│   ├── test_board.py
│   ├── test_pattern.py
│   ├── test_human.py
│   ├── test_encoder.py
│   ├── test_neural_model.py
│   └── test_neural_mcts.py
├── board.py
├── human.py
├── main.py
├── gui.py
├── requirements.txt
└── AI_ENGINEERING_ROADMAP.md
```

---

## 4. 阶段 0：工程基线整理

目标：保证项目可以稳定安装、测试、训练和保存产物。

### 4.1 Todo

- [x] 确认现有单元测试通过
- [x] 准备 `requirements.txt`
- [x] 创建 `data/selfplay/`
- [x] 创建 `models/checkpoints/`
- [x] 增加 `.gitignore`，忽略缓存和大模型产物
- [ ] 确认 `Training/output/` 是否要继续纳入版本管理
- [ ] 给 README 增加“AI 演进路线”入口，链接到本文档

### 4.2 推荐 `.gitignore`

如果项目还没有 `.gitignore`，建议加入：

```gitignore
__pycache__/
*.pyc
.DS_Store
.venv/
data/selfplay/*.npz
models/*.pt
models/checkpoints/*.pt
Training/output/*.json
Training/output/*.csv
```

注意：如果你希望保留一些小型训练结果作为示例，可以不要忽略 `Training/output/`，或者只保留明确命名的样例文件。

### 4.3 教程命令

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/selfplay models/checkpoints
python -m unittest discover -s tests
```

### 4.4 验收标准

- [ ] `python -m unittest discover -s tests` 通过
- [ ] `python -c "import numpy, torch, tqdm"` 不报错
- [ ] `data/selfplay/` 存在
- [ ] `models/checkpoints/` 存在

---

## 5. 阶段 1：完善现有局面编码器

目标：保留当前三通道相对视角设计，将 `AI/encoder.py` 完善为能稳定接入 PyTorch 策略价值网络和神经网络 MCTS 的模块。

建议新增文件：

```text
AI/encoder.py
tests/test_encoder.py
```

### 5.1 Todo

- [x] 新增 `AI/encoder.py`
- [x] 实现三通道局面编码
- [x] 当前行棋方使用 `board.cnt_player`
- [x] 第 0 层表示当前行棋方棋子
- [x] 第 1 层表示对手棋子
- [x] 第 2 层表示当前行棋方颜色：黑棋全 `1`，白棋全 `0`
- [x] 实现二维合法落子 mask：空位为 `1`，已占用位置为 `0`
- [x] 实现 `move_to_index(move)`
- [x] 实现 `index_to_move(index)`
- [x] 为 `move_to_index()` 增加坐标类型与越界校验
- [x] 为 `index_to_move()` 增加类型与范围校验
- [x] 增加 `Code.to_numpy()`，返回 `numpy.ndarray`，`dtype=np.float32`
- [x] 增加 `encode_board(board)`，直接返回 `numpy.float32` 编码数组
- [x] `legal_move_mask(board)` 默认返回一维策略 mask
- [x] `legal_move_mask(board, flatten=False)` 支持返回二维棋盘 mask
- [x] 增加 `get_code(board)` 作为数组返回的兼容别名
- [x] 为编码器补充 `tests/test_encoder.py`
- [x] 确认黑白双方视角编码一致

### 5.2 当前实现状态

当前文件继续使用 `Code` 类承载编码结果，同时提供数组接口：

```python
encoded = encoder(board)
state = encoded.to_numpy()
move_index = encoded.move_to_index((row, col))
move = encoded.index_to_move(move_index)
policy_mask = legal_move_mask(board)
mask_2d = legal_move_mask(board, flatten=False)
```

这个设计可以继续使用。当前实测已通过以下局面：

```text
黑棋行棋：
  第 0 层只标记黑棋
  第 1 层只标记白棋
  第 2 层全为 1

白棋行棋：
  第 0 层只标记白棋
  第 1 层只标记黑棋
  第 2 层全为 0

已落子位置：
  legal_move_mask 对应位置为 0
```

当前编码语义、数组转换、mask 和索引校验均已完成。后续如果没有特殊需求，不需要继续修改编码器，可以直接进入策略价值网络阶段。

### 5.3 设计说明

推荐输入张量格式：

```text
shape = (3, board_size, board_size)
```

三层含义：

```text
plane 0：当前玩家自己的棋子
plane 1：对手棋子
plane 2：当前玩家颜色标记
```

如果 `player == 1`，第三层可以全是 `1.0`；如果 `player == 2`，第三层可以全是 `0.0`。也可以反过来，但必须保持全项目一致。

动作索引：

```python
index = row * size + col
row = index // size
col = index % size
```

这样 15x15 棋盘的策略输出就是 225 个 logits。

注意：第 0、1 层里的数值 `1` 只表示“该层代表的玩家在这个位置有棋子”。棋子所属阵营由所在层表达，不能在这些通道里继续使用棋盘原始值 `1` 和 `2`。

### 5.4 当前接口与训练适配

推荐训练代码直接使用 `encode_board(board)`：

```python
from AI.encoder import encode_board, legal_move_mask

state = encode_board(board)
policy_mask = legal_move_mask(board)
```

转换后的格式必须满足：

```text
state.shape       == (3, size, size)
policy_mask.shape == (size * size,)
```

如果需要二维 mask 进行可视化或调试：

```python
mask_2d = legal_move_mask(board, flatten=False)
```

如果需要坐标和策略索引转换：

```python
encoded = encoder(board)
index = encoded.move_to_index((row, col))
move = encoded.index_to_move(index)
```

`encode_board()` 返回 `numpy.float32`，可以直接在训练代码中转换成 PyTorch tensor：

```python
state_tensor = torch.from_numpy(encode_board(board))
```

### 5.5 已完成的输入校验

动作转换现在会拒绝非法输入。例如在 15x15 棋盘中：

```python
encoded.move_to_index((-1, 0))  # ValueError
encoded.move_to_index((15, 0))  # ValueError
encoded.index_to_move(225)      # ValueError
```

当前校验规则：

```text
move_to_index：
  输入必须是两个整数
  row 和 col 必须在 [0, size) 内

index_to_move：
  输入必须是整数
  index 必须在 [0, size * size) 内
```

非法输入统一抛出 `ValueError`，避免训练时产生静默错误。

### 5.6 当前推荐接口

```python
def encoder(board: Board) -> Code:
    """Return a Code container with board encoding and index helpers."""

def encode_board(board: Board) -> np.ndarray:
    """Return a float32 array with shape (3, size, size)."""

def legal_move_mask(board: Board, flatten: bool = True) -> np.ndarray:
    """Return float32 mask: 1 for legal moves and 0 for occupied moves."""

class Code:
    def to_numpy(self) -> np.ndarray:
        """Return the encoded state as float32 ndarray."""

    def move_to_index(self, move: tuple[int, int]) -> int:
        """Convert a valid board coordinate into a policy index."""

    def index_to_move(self, index: int) -> tuple[int, int]:
        """Convert a valid policy index into a board coordinate."""
```

`get_code(board)` 是 `encode_board(board)` 的兼容别名。

### 5.7 教程命令

```bash
python -m unittest tests.test_encoder
python -m unittest discover -s tests
```

### 5.8 验收标准

- [x] 15x15 棋盘可以构造三通道编码
- [x] 5x5 棋盘可以构造三通道编码
- [x] `(7, 7)` 在 15x15 上能映射成 `112`
- [x] index `112` 在 15x15 上能映射回 `(7, 7)`
- [x] 已占用位置在二维 legal mask 中为 `0`
- [x] 空位在二维 legal mask 中为 `1`
- [x] 编码转换后为 `np.float32`，shape 为 `(3, size, size)`
- [x] 策略使用的一维 mask shape 为 `(size * size,)`
- [x] 黑棋视角与白棋视角均有单元测试
- [x] 索引转换的合法和非法输入均有单元测试
- [x] 满棋盘 mask 全为 `0`

---

## 6. 阶段 2：实现策略价值网络

目标：让模型同时学习“这个局面应该下哪里”和“这个局面对当前玩家有多好”。

建议新增文件：

```text
AI/neural_model.py
tests/test_neural_model.py
```

### 6.1 Todo

- [ ] 新增 `AI/neural_model.py`
- [ ] 实现 `PolicyValueNet`
- [ ] policy head 输出 `size * size` 个 logits
- [ ] value head 输出一个 `[-1, 1]` 区间的值
- [ ] 支持保存 checkpoint
- [ ] 支持加载 checkpoint
- [ ] 为模型输入输出 shape 补测试

### 6.2 推荐模型结构

初版不要直接上复杂 ResNet。建议先用小 CNN，保证训练管线跑通。

```text
输入：batch x 3 x size x size
  -> Conv + BatchNorm + ReLU
  -> Conv + BatchNorm + ReLU
  -> Conv + BatchNorm + ReLU
  -> policy head：batch x size*size
  -> value head：batch x 1
```

### 6.3 损失函数

总损失：

```text
total_loss = policy_loss + value_loss + l2_reg
```

其中：

```text
policy_loss：交叉熵或 soft target cross entropy
value_loss：MSE
l2_reg：权重衰减，由 optimizer 的 weight_decay 处理
```

如果 policy target 是 MCTS visit 分布，使用 soft target：

```python
policy_loss = -(target_policy * log_probs).sum(dim=1).mean()
```

如果 policy target 只有单个老师落点，可以先用普通交叉熵。

### 6.4 教程命令

```bash
python -m unittest tests.test_neural_model
python -c "from AI.neural_model import PolicyValueNet; model = PolicyValueNet(15); print(model)"
```

### 6.5 验收标准

- [ ] 输入 `batch=2, size=15` 时，policy 输出 shape 为 `(2, 225)`
- [ ] value 输出 shape 为 `(2, 1)` 或 `(2,)`
- [ ] value 数值经过 `tanh` 限制在 `[-1, 1]`
- [ ] 模型可以保存到 `models/checkpoints/test.pt`
- [ ] 模型可以从 checkpoint 加载

---

## 7. 阶段 3：生成冷启动自我对弈数据

目标：先用现有强规则 AI 生成训练数据，让神经网络有一个初始水平。

建议新增文件：

```text
Training/self_play.py
```

### 7.1 Todo

- [ ] 新增 `Training/self_play.py`
- [ ] 支持命令行参数 `--games`
- [ ] 支持命令行参数 `--size`
- [ ] 支持命令行参数 `--out`
- [ ] 支持命令行参数 `--teacher`
- [ ] 保存 `states`
- [ ] 保存 `policies`
- [ ] 保存 `values`
- [ ] 保存元信息，比如棋盘大小、老师类型、随机种子
- [ ] 生成数据后能被训练脚本读取

### 7.2 数据格式

建议 `.npz` 内包含：

```text
states：float32，shape = (N, 3, size, size)
policies：float32，shape = (N, size * size)
values：float32，shape = (N,)
metadata：可选，json 字符串
```

每一步都从当前玩家视角保存局面。最终胜负要转换成当前样本玩家视角：

```text
当前样本玩家最终赢：value = 1
当前样本玩家最终输：value = -1
平局：value = 0
```

### 7.3 第一版 teacher 策略

先用现有 `HeuristicAIDepth` 生成单点策略：

```text
teacher 选择 move
policy[move_to_index(move)] = 1.0
```

后面接神经网络 MCTS 后，再把 policy 改成 MCTS visit 分布。

### 7.4 教程命令

快速调试建议先用小棋盘：

```bash
python Training/self_play.py \
  --games 10 \
  --size 9 \
  --teacher heuristic-depth2 \
  --out data/selfplay/bootstrap_9x9.npz
```

15x15 数据：

```bash
python Training/self_play.py \
  --games 100 \
  --size 15 \
  --teacher heuristic-depth2 \
  --out data/selfplay/bootstrap_15x15.npz
```

### 7.5 验收标准

- [ ] 能生成 `.npz` 文件
- [ ] `states.shape[0] == policies.shape[0] == values.shape[0]`
- [ ] `states.shape[1:] == (3, size, size)`
- [ ] `policies.shape[1] == size * size`
- [ ] 每个 policy 的和接近 `1.0`
- [ ] values 只包含 `-1`、`0`、`1` 或合理浮点值

---

## 8. 阶段 4：训练策略价值网络

目标：用自我对弈数据训练 `PolicyValueNet`。

建议新增文件：

```text
Training/train_policy_value.py
```

### 8.1 Todo

- [ ] 新增 `Training/train_policy_value.py`
- [ ] 支持读取 `.npz` 数据
- [ ] 实现 PyTorch Dataset
- [ ] 实现 DataLoader
- [ ] 实现 policy loss
- [ ] 实现 value loss
- [ ] 实现 optimizer
- [ ] 支持 `--epochs`
- [ ] 支持 `--batch-size`
- [ ] 支持 `--lr`
- [ ] 支持 `--model-out`
- [ ] 每个 epoch 打印 loss
- [ ] 保存 checkpoint

### 8.2 训练命令

```bash
python Training/train_policy_value.py \
  --data data/selfplay/bootstrap_15x15.npz \
  --epochs 20 \
  --batch-size 64 \
  --lr 0.001 \
  --model-out models/checkpoints/pvnet_bootstrap.pt
```

如果电脑性能一般，可以先用 9x9：

```bash
python Training/train_policy_value.py \
  --data data/selfplay/bootstrap_9x9.npz \
  --epochs 10 \
  --batch-size 32 \
  --lr 0.001 \
  --model-out models/checkpoints/pvnet_9x9.pt
```

### 8.3 训练注意事项

- 先把 pipeline 跑通，不要一开始追求棋力。
- 先用小棋盘验证，再回到 15x15。
- loss 能下降即可进入下一阶段。
- 如果 policy loss 不下降，先检查 `move_to_index` 和 `index_to_move`。
- 如果 value loss 不下降，先检查胜负标签是否按“当前样本玩家视角”生成。

### 8.4 验收标准

- [ ] 训练脚本能正常启动
- [ ] 一个 epoch 能完整跑完
- [ ] loss 被打印到终端
- [ ] checkpoint 被保存
- [ ] checkpoint 能重新加载
- [ ] 对同一局面，模型能输出 policy 和 value

---

## 9. 阶段 5：实现神经网络 MCTS

目标：把当前随机 MCTS 升级为神经网络引导的搜索。

建议新增文件：

```text
AI/NeuralMCTS_ai.py
tests/test_neural_mcts.py
```

### 9.1 Todo

- [ ] 新增 `AI/NeuralMCTS_ai.py`
- [ ] 加载 `PolicyValueNet`
- [ ] 使用 `encode_board`
- [ ] 使用 legal mask 屏蔽非法落点
- [ ] 用 policy 输出初始化 child prior
- [ ] 用 value 输出替代随机 rollout
- [ ] 实现 PUCT 选择公式
- [ ] 实现 temperature 控制落子随机性
- [ ] 支持 `simulations` 参数
- [ ] 支持 `model_path` 参数
- [ ] 补合法落子测试

### 9.2 PUCT 公式

每个子节点得分：

```text
score = Q + U
Q = child.value / child.visits
U = c_puct * child.prior * sqrt(parent.visits) / (1 + child.visits)
```

如果 `child.visits == 0`，`Q` 可以先设为 `0`。

### 9.3 搜索流程

```text
1. 从 root 开始
2. selection：用 PUCT 选子节点
3. expansion：遇到叶子节点时，用神经网络预测 policy 和 value
4. mask：把非法落点概率清零
5. normalize：重新归一化合法落点概率
6. backup：把 value 沿路径回传，每上一层取反
7. move selection：根据 root children 的 visit count 选最终落点
```

### 9.4 与现有 MCTS 的差异

当前 `MCTS_AI`：

```text
随机扩展 + 随机 rollout + UCT
```

目标 `NeuralMCTS_AI`：

```text
policy prior 扩展 + value 评估 + PUCT
```

这一步是项目从“搜索 AI”变成“学习型搜索 AI”的关键。

### 9.5 教程命令

```bash
python -m unittest tests.test_neural_mcts
python -c "from board import Board; from AI.NeuralMCTS_ai import NeuralMCTS_AI; ai = NeuralMCTS_AI(Board(15), 1, model_path='models/checkpoints/pvnet_bootstrap.pt'); print(ai.get_move())"
```

### 9.6 验收标准

- [ ] 空棋盘返回中心附近合法点
- [ ] 非空棋盘返回合法点
- [ ] 满棋盘返回 `None`
- [ ] 不会选择已占用位置
- [ ] 在一手必胜局面优先直接赢
- [ ] 在对手一手必胜局面优先防守

---

## 10. 阶段 6：建立模型评测系统

目标：用胜率和固定对手评估模型，而不是凭感觉判断模型变强。

建议新增文件：

```text
Training/evaluate.py
```

### 10.1 Todo

- [ ] 新增 `Training/evaluate.py`
- [ ] 支持 `--model`
- [ ] 支持 `--games`
- [ ] 支持 `--size`
- [ ] 支持 `--opponent`
- [ ] 支持 `--seed`
- [ ] 支持黑白互换
- [ ] 输出 wins、losses、draws、win_rate
- [ ] 保存评测 JSON 到 `Training/output/`

### 10.2 推荐对手矩阵

- [ ] `NeuralMCTS_AI` vs `HeuristicAIDepth(depth=1)`
- [ ] `NeuralMCTS_AI` vs `HeuristicAIDepth(depth=2)`
- [ ] `NeuralMCTS_AI` vs `HeuristicAIDepth(depth=3)`
- [ ] `NeuralMCTS_AI` vs `MCTS_AI(times=500)`
- [ ] `NeuralMCTS_AI` vs `MCTS_AI(times=1000)`

### 10.3 教程命令

```bash
python Training/evaluate.py \
  --model models/checkpoints/pvnet_bootstrap.pt \
  --games 40 \
  --size 15 \
  --opponent heuristic-depth2 \
  --seed 42
```

预期输出格式：

```text
wins=23 losses=14 draws=3 win_rate=0.575
```

### 10.4 验收标准

- [ ] 同一 seed 下评测结果可复现
- [ ] 黑白双方各下约一半局数
- [ ] 非法落子直接判负并记录
- [ ] 评测结果保存为 JSON
- [ ] 输出中包含模型路径、对手、棋盘大小、局数、seed

---

## 11. 阶段 7：接入命令行和 GUI

目标：用户可以直接选择神经网络 AI 对战。

### 11.1 CLI Todo

修改文件：

```text
main.py
```

任务：

- [ ] AI 类型选择增加第 3 项：`Neural MCTS AI`
- [ ] 询问模型路径，默认 `models/best.pt`
- [ ] 询问 MCTS simulations，默认可以先设为 `200`
- [ ] 构造 `NeuralMCTS_AI`
- [ ] 确保人类执黑或执白都能工作

命令行提示建议：

```text
Choose AI type:
  1: HeuristicAI (depth search)
  2: MCTS AI (Monte Carlo Tree Search)
  3: Neural MCTS AI
```

### 11.2 GUI Todo

修改文件：

```text
gui.py
```

任务：

- [ ] AI 类型弹窗增加第 3 项
- [ ] 增加模型路径输入框
- [ ] 增加 simulations 输入框
- [ ] `_build_ai()` 支持 `neural_mcts`
- [ ] restart 后重新加载或复用模型
- [ ] AI 思考时间较长时，状态栏显示 `AI Thinking...`

### 11.3 验收标准

- [ ] `python main.py` 可以选择神经网络 AI
- [ ] `python gui.py` 可以选择神经网络 AI
- [ ] 模型路径不存在时有清晰报错
- [ ] 神经网络 AI 落子合法
- [ ] 游戏结束时仍能正常提示胜负

---

## 12. 阶段 8：实现 AlphaZero 式训练循环

目标：让模型通过自我对弈持续迭代，而不是只学习固定老师。

建议新增文件：

```text
Training/az_loop.py
```

### 12.1 Todo

- [ ] 新增 `Training/az_loop.py`
- [ ] 加载当前最佳模型 `models/best.pt`
- [ ] 自我对弈生成数据
- [ ] 训练候选模型
- [ ] 候选模型对战旧最佳模型
- [ ] 胜率达标后替换 `models/best.pt`
- [ ] 保存每轮训练数据
- [ ] 保存每轮候选模型
- [ ] 保存每轮评测结果
- [ ] 保存总历史 `Training/output/az_history.csv`

### 12.2 循环流程

```text
for iteration in range(iterations):
    1. 用 best model 自我对弈，生成 data/selfplay/iter_N.npz
    2. 用历史数据或最近 K 轮数据训练 candidate model
    3. candidate vs best 评测
    4. 如果 candidate 胜率 >= 55%，替换 best
    5. 记录结果
```

### 12.3 推荐命令

先用 9x9 调通：

```bash
python Training/az_loop.py \
  --iterations 3 \
  --games-per-iter 20 \
  --epochs 3 \
  --eval-games 20 \
  --size 9
```

再扩到 15x15：

```bash
python Training/az_loop.py \
  --iterations 20 \
  --games-per-iter 100 \
  --epochs 5 \
  --eval-games 40 \
  --size 15
```

### 12.4 晋级规则

建议第一版：

```text
candidate win_rate >= 0.55 -> 替换 best
candidate win_rate < 0.55 -> 保留 old best
```

更稳的版本：

```text
candidate win_rate >= 0.55 且非法落子为 0 -> 替换 best
```

### 12.5 验收标准

- [ ] 能完成至少 1 个完整 iteration
- [ ] 每轮会生成 `.npz` 数据
- [ ] 每轮会生成候选模型 checkpoint
- [ ] 每轮会生成评测结果 JSON
- [ ] `az_history.csv` 记录每轮胜率
- [ ] 达到晋级规则时会更新 `models/best.pt`

---

## 13. 阶段 9：性能优化和稳定性

目标：在功能跑通后提升训练速度、搜索质量和可复现性。

### 13.1 Todo

- [ ] 使用 `Board.create_key()` 增加 MCTS 转置表
- [ ] 神经网络推理增加 batch 模式
- [ ] self-play 增加并行生成
- [ ] 增加棋盘旋转和翻转数据增强
- [ ] 给所有训练脚本增加 seed 控制
- [ ] 保存训练配置到 checkpoint
- [ ] 保存模型版本号和训练数据来源
- [ ] 记录每局平均步数
- [ ] 记录每步平均搜索时间
- [ ] 增加超时保护，避免 GUI 卡死

### 13.2 数据增强规则

五子棋棋盘可以做 8 种对称增强：

```text
原图
旋转 90 度
旋转 180 度
旋转 270 度
水平翻转
垂直翻转
主对角线翻转
副对角线翻转
```

注意：增强时必须同时变换 policy 分布，否则训练标签会错。

### 13.3 验收标准

- [ ] 同样 simulations 下，神经网络 MCTS 搜索更快或棋力更强
- [ ] self-play 能稳定生成上百局
- [ ] 训练可以复现
- [ ] checkpoint 能追溯训练配置
- [ ] GUI 不会因为 AI 思考长时间无响应

---

## 14. 建议开发顺序

### 14.1 第一优先级：跑通学习闭环

- [ ] 阶段 0：工程基线整理
- [ ] 阶段 1：局面编码器
- [ ] 阶段 2：策略价值网络
- [ ] 阶段 3：冷启动自我对弈数据
- [ ] 阶段 4：训练策略价值网络

完成后，项目已经具备“从数据中学习”的能力。

### 14.2 第二优先级：让模型参与决策

- [ ] 阶段 5：神经网络 MCTS
- [ ] 阶段 6：模型评测系统
- [ ] 阶段 7：接入 CLI 和 GUI

完成后，用户可以真正和神经网络 AI 对战。

### 14.3 第三优先级：让模型自己进化

- [ ] 阶段 8：AlphaZero 式训练循环
- [ ] 阶段 9：性能优化和稳定性

完成后，项目才进入“持续自我提升”的方向。

---

## 15. 推荐里程碑

### Milestone 1：监督学习冷启动

目标：用现有启发式 AI 生成数据并训练第一个模型。

- [ ] 完成 `AI/encoder.py`
- [ ] 完成 `AI/neural_model.py`
- [ ] 完成 `Training/self_play.py`
- [ ] 完成 `Training/train_policy_value.py`
- [ ] 生成 `models/checkpoints/pvnet_bootstrap.pt`

验收命令：

```bash
python Training/self_play.py --games 20 --size 9 --teacher heuristic-depth2 --out data/selfplay/bootstrap_9x9.npz
python Training/train_policy_value.py --data data/selfplay/bootstrap_9x9.npz --epochs 5 --batch-size 32 --model-out models/checkpoints/pvnet_9x9.pt
python -m unittest discover -s tests
```

### Milestone 2：神经网络参与搜索

目标：神经网络 MCTS 可以返回合法落子，并能和现有 AI 对战。

- [ ] 完成 `AI/NeuralMCTS_ai.py`
- [ ] 完成 `tests/test_neural_mcts.py`
- [ ] 完成 `Training/evaluate.py`
- [ ] 评测 `NeuralMCTS_AI` vs `HeuristicAIDepth`

验收命令：

```bash
python Training/evaluate.py --model models/checkpoints/pvnet_9x9.pt --games 20 --size 9 --opponent heuristic-depth2
```

### Milestone 3：接入产品入口

目标：命令行和 GUI 都可以选择神经网络 AI。

- [ ] 修改 `main.py`
- [ ] 修改 `gui.py`
- [ ] 增加模型路径输入
- [ ] 增加 simulations 输入
- [ ] 手动完成一局人机对战

验收命令：

```bash
python main.py
python gui.py
```

### Milestone 4：自我进化闭环

目标：模型可以通过自我对弈、训练、评测自动迭代。

- [ ] 完成 `Training/az_loop.py`
- [ ] 生成至少 3 轮训练记录
- [ ] 保存 `models/best.pt`
- [ ] 保存 `Training/output/az_history.csv`

验收命令：

```bash
python Training/az_loop.py --iterations 3 --games-per-iter 20 --epochs 3 --eval-games 20 --size 9
```

---

## 16. 质量要求

所有阶段都要遵守下面规则：

- [ ] 每新增一个核心模块，就新增对应测试
- [ ] 所有 AI 返回的 move 必须经过 `Board.is_legal_move(move)` 校验
- [ ] 所有训练脚本都必须支持命令行参数
- [ ] 所有训练产物都必须写入固定目录
- [ ] 所有评测都必须记录 seed
- [ ] 所有模型 checkpoint 都必须能重新加载
- [ ] 每次完成阶段任务后运行 `python -m unittest discover -s tests`

---

## 17. 不建议过早做的事情

这些事情有价值，但不适合在学习闭环跑通前做：

- [ ] 黑棋禁手规则
- [ ] 交换规则
- [ ] 开局库
- [ ] 复杂 GUI 重构
- [ ] 大型 ResNet
- [ ] 分布式训练
- [ ] Elo 排名系统
- [ ] 复杂数据库

原因：这些会增加工程复杂度，但不能直接解决“模型是否能从数据中学习并提升棋力”的核心问题。

---

## 18. 每次开发完成后的记录模板

完成一个任务后，在这里追加记录：

```markdown
## YYYY-MM-DD

- 完成：
- 修改文件：
- 验证命令：
- 结果：
- 遗留问题：
```

### 开发记录

暂无。
