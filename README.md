**中文README附在英文README后面，供中文用户参考。英文README是主版本，中文README会定期同步更新。**
# 🎯 Gomoku – Python Implementation

A pure Python implementation of the classic Gomoku (Five in a Row) board game. No third‑party libraries required. The game supports customizable board sizes, two‑player mode, and multiple built‑in AI opponents with different strategies. The project is structured to allow future extensions toward a self‑training reinforcement learning AI.

---

## ✨ Current Features

- ✅ Pure Python – zero external dependencies
- ✅ Customizable board size (default 15×15)
- ✅ Clean console board display with row/column labels
- ✅ Fast win detection based on the last move only (O(1) complexity)
- ✅ Robust input validation and error messages
- ✅ Draw detection (when the board is full)
- ✅ **Human vs AI mode** with multiple AI difficulties:
  - `HeuristicAI` – greedy one‑step pattern scoring
  - `HeuristicAIDepth2` – 2‑ply minimax search (stronger)
- ✅ **Unified player interface**: human and AI players are treated identically by the game loop, making it easy to add new AI opponents
- ✅ Incremental board evaluation for fast move scoring (only affected lines recomputed)

---

## 🚀 Quick Start

### Run the Game

```bash
python main.py
```

### Game Mode Selection

Upon starting, you can choose:
- **Two‑Player Mode**: two human players take turns.
- **Human vs AI Mode**: play against the AI, choose your side, and select the AI difficulty.

### Rules

- Player 1 uses **1**, Player 2 uses **2**
- Players take turns entering coordinates in the format: `row column` (both starting from 1)
- The first player to align five pieces horizontally, vertically, or diagonally wins

### Example Game (Human vs AI)

```
Welcome to Gomoku!
Choose board size (default 15): 15
Do you want to play against the AI? (y/n): y
Do you want to be Player 1 or Player 2? (Enter 1 or 2): 1
Choose AI difficulty: 1 for Heuristic AI, 2 for Depth2 AI: 2
  1  2  3  4  5 ...
1  0  0  0  0  0 ...
...
Player 1's turn.
Enter your move (row col): 8 8
Player 2's turn.
AI (Depth2) placed a piece at (9, 9).
...
```

---

## 📁 Project Structure

```
.
├── main.py                       # Main program – game loop and user interaction
├── board.py                      # Board class (board state, move validation, win detection)
├── human.py                      # Human player class (console input)
├── AI/
│   ├── base.py                   # Abstract base class for all AI players
│   ├── Heuristic_ai.py           # Greedy one‑step heuristic AI
│   └── Heuristic_ai_depth2.py    # 2‑ply minimax heuristic AI (stronger)
└── README.md                     # Project documentation
```

> *Note: All game‑specific logic (Board, players, AI) is now cleanly separated into dedicated modules.*

---

## 🔧 Core Classes

### `Board(size=15)`

| Method                               | Description                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `place(player, [row, col])`          | Places a piece at the given position. Returns `True` if successful. Indices are 0‑based.   |
| `check_win(player, [row, col])`      | Checks whether the specified player has won after placing a piece at `[row, col]`.         |
| `print_board()`                      | Prints the current board state with row and column labels.                                  |

### `BaseAI` (Abstract Base Class)

All AI players inherit from `BaseAI`, which defines the required interface:

| Method                 | Description                                                                    |
| ---------------------- | ------------------------------------------------------------------------------ |
| `get_move()`           | Returns a `(row, col)` tuple representing the AI's chosen move, or `None` if no moves are available. |
| `make_move()`          | Executes the move by calling `get_move()` and placing the piece on the board.   |

### `HeuristicAI(BaseAI)`

A greedy scoring AI that evaluates the board by scanning only the four lines passing through each candidate move. It balances offensive and defensive pattern scores (open two, open three, etc.) using a configurable weight, making it fast and reasonably effective.

### `HeuristicAIDepth2(BaseAI)`

An improved version using a **2‑ply minimax search** with the same pattern‑based evaluation. The AI simulates its own move and the opponent's best counter‑move, then chooses the move that maximizes its advantage under worst‑case assumptions. Candidate pruning (only cells near existing stones) keeps the search fast. This AI shows better defensive awareness and can perform simple forced sequences.

### `Human(BaseAI)`

Implements the same interface as AI players, obtaining moves from console input. This design allows the game loop to treat human and AI players uniformly.

---

## 🧠 Future Roadmap (Towards a Self‑Training Gomoku AI)

### 📌 Phase 1: Heuristic AI Foundation ✅
- [x] Board evaluation via pattern recognition
- [x] Greedy one‑step AI opponent
- [x] 2‑ply minimax AI with incremental evaluation
- [x] Human vs AI gameplay
- [x] Modular player interface for easy AI swapping

### 📌 Phase 2: Stronger Search & Automatic Tuning
- [ ] Add alpha‑beta pruning for deeper search (4‑6 ply)
- [ ] Implement terminal state detection (immediate win/loss) in search
- [ ] Use genetic algorithms to automatically tune scoring weights
- [ ] Add more sophisticated patterns (jump‑three, jump‑four, double‑threat recognition)

### 📌 Phase 3: Deep Reinforcement Learning (AlphaZero Style)
- [ ] Build a residual neural network (policy + value heads) using PyTorch
- [ ] Implement Monte Carlo Tree Search (MCTS)
- [ ] Multi‑channel board state encoding

### 📌 Phase 4: Self‑Play and Data Generation
- [ ] Self‑play data generator
- [ ] Replay buffer implementation
- [ ] Training loop with policy loss and value loss

### 📌 Phase 5: Full Self‑Training Pipeline
- [ ] Automated iteration: self‑play → training → evaluation → model update
- [ ] Model checkpoint saving and loading
- [ ] Training visualization (win rate curves, loss curves)

---

## ⚠️ Current Limitations & Near‑Term Improvements

While the current AI is already a challenging opponent for casual players, it has clear limitations that will be addressed in future updates:

1. **No explicit win/loss detection in search** – The AI does not assign a terminal value when a five‑in‑a‑row is formed, causing it to sometimes overlook immediate winning moves or forced losses.  
   *Plan: add terminal detection in all search nodes.*

2. **Fixed search depth** – The 2‑ply minimax AI cannot see longer forced sequences (e.g., VCF – continuous forcing moves).  
   *Plan: implement alpha‑beta pruning to allow depths of 4‑6 ply within reasonable time.*

3. **Hand‑tuned scoring weights** – Pattern scores are manually set and may be suboptimal.  
   *Plan: apply genetic algorithms or other optimization methods to automatically discover better weights.*

4. **Limited pattern set** – Only continuous lines are considered; jump‑three, jump‑four, and double‑threat patterns are missing.  
   *Plan: extend the pattern library for finer positional judgment.*

5. **No position opening book** – The AI has no special knowledge for the opening phase.  
   *Plan: add a small opening book or use self‑play data to learn openings.*

---

## 🤝 Contributing

Issues and Pull Requests are welcome! Areas where contributions are especially appreciated:

- Improving AI scoring weights or adding more sophisticated patterns
- Implementing additional AI difficulty levels (e.g., MCTS‑based AI)
- Enhancing console UI (screen clearing, prettier piece symbols)
- Adding undo, game saving, and replay functionality
- Implementing standard professional rules (black forbidden moves, swap opening, etc.)
- Writing unit tests for the AI module

---

**Enjoy the game! 🎲**



# 🎯 Gomoku (五子棋) – Python 实现

一个纯 Python 实现的五子棋游戏，无需任何第三方库。支持自定义棋盘大小、双人对战，并内置多个不同策略的 AI 对手。项目已为后续强化学习扩展预留接口。

---

## ✨ 当前功能

- ✅ 纯 Python 实现，零外部依赖
- ✅ 可自定义棋盘尺寸（默认 15×15）
- ✅ 清晰的控制台棋盘显示（带行列号）
- ✅ 基于最后落子位置的快速赢棋检测（O(1) 复杂度）
- ✅ 完善的输入校验与错误提示
- ✅ 平局检测（棋盘下满）
- ✅ **人机对战模式**，提供多种 AI 难度：
  - `HeuristicAI` – 贪心一步评分
  - `HeuristicAIDepth2` – 2层极小极大搜索（更强）
- ✅ **统一的玩家接口**：人类与 AI 被同等对待，易于增加新的 AI 对手
- ✅ 增量棋盘评估：每次只计算落子点相关线条的分数变化，大幅提高搜索速度

---

## 🚀 快速开始

### 运行游戏

```bash
python main.py
```

### 游戏模式选择

启动后可选择：
- **双人对战**：两名人类玩家轮流落子。
- **人机对战**：选择与 AI 对战，指定自己执先手或后手，并选择 AI 难度。

### 游戏规则

- 玩家 1 执 **1**，玩家 2 执 **2**
- 轮流输入落子坐标，格式：`行 列`（行列均从 1 开始计数）
- 率先在横、竖、斜任一方向连成五子者获胜

### 示例对局（人机对战）

```
Welcome to Gomoku!
Choose board size (default 15): 15
Do you want to play against the AI? (y/n): y
Do you want to be Player 1 or Player 2? (Enter 1 or 2): 1
Choose AI difficulty: 1 for Heuristic AI, 2 for Depth2 AI: 2
  1  2  3  4  5 ...
1  0  0  0  0  0 ...
...
Player 1's turn.
Enter your move (row col): 8 8
Player 2's turn.
AI (Depth2) placed a piece at (9, 9).
...
```

---

## 📁 项目结构

```
.
├── main.py                       # 主程序，游戏循环与用户交互
├── board.py                      # Board 类（棋盘状态、落子验证、胜负判断）
├── human.py                      # 人类玩家类（控制台输入）
├── AI/
│   ├── base.py                   # 所有 AI 的抽象基类
│   ├── Heuristic_ai.py           # 贪心一步启发式 AI
│   └── Heuristic_ai_depth2.py    # 2层极小极大启发式 AI（更强）
└── README.md                     # 项目说明文档
```

> *注：游戏逻辑 (Board, players, AI) 现已完全分离到各自模块，架构更清晰。*

---

## 🔧 核心类说明

### `Board(size=15)`

| 方法                                 | 描述                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `place(player, [row, col])`          | 在指定位置落子，返回是否成功。行列索引从 0 开始。                            |
| `check_win(player, [row, col])`      | 检测指定玩家在最新落子后是否获胜（仅检查落子点四个方向）。                    |
| `print_board()`                      | 在控制台打印当前棋盘状态（带行列号）。                                        |

### `BaseAI` (抽象基类)

所有 AI 均继承自 `BaseAI`，它规定了必须实现的接口：

| 方法                   | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `get_move()`           | 返回 AI 选择的落子坐标 `(row, col)`，若无合法位置则返回 `None`。 |
| `make_move()`          | 调用 `get_move()` 并在棋盘上落子。                            |

### `HeuristicAI(BaseAI)`

贪心一步评分 AI，只评估候选落子点四个方向上的棋形模式（活二、活三、活四等），平衡攻防分数后选择综合分最高的位置。评估速度快，具备基本的进攻和防守意识。

### `HeuristicAIDepth2(BaseAI)`

增强版 AI，采用 **2 层极小极大搜索** 结合相同的棋形评分。它会模拟自己的一步和对手的最佳应对，在最不利的情况下仍能保持优势。通过仅搜索棋子周边空位（候选点剪枝）并使用增量评估，搜索速度仍然很快。该 AI 防守意识更强，能执行简单的连续攻击。

### `Human(BaseAI)`

实现了与 AI 相同的接口，通过控制台获取用户输入。使游戏循环可以无差别处理人类与 AI 玩家。

---

## 🧠 未来扩展路线（自训练五子棋 AI）

### 📌 第一阶段：启发式 AI 基础 ✅
- [x] 实现棋盘局面评分函数（连子模式识别）
- [x] 贪心一步 AI 对手
- [x] 2层极小极大搜索 AI（增量评估）
- [x] 支持人机对战模式
- [x] 模块化玩家接口，便于替换不同 AI

### 📌 第二阶段：更强的搜索与自动调参
- [ ] 添加 Alpha‑Beta 剪枝，支持 4‑6 层搜索
- [ ] 在搜索中加入终局（必胜/必败）检测
- [ ] 使用遗传算法自动优化评分权重
- [ ] 增加更丰富的棋形（跳活三、跳冲四、双重威胁等）

### 📌 第三阶段：深度强化学习（AlphaZero 风格）
- [ ] 使用 PyTorch 构建残差神经网络（策略+价值双输出）
- [ ] 实现蒙特卡洛树搜索（MCTS）
- [ ] 完成棋盘状态的多通道编码

### 📌 第四阶段：自我对弈与数据生成
- [ ] 实现模型自我对弈数据生成器
- [ ] 构建经验回放池（Replay Buffer）
- [ ] 编写训练循环（策略损失 + 价值损失）

### 📌 第五阶段：完整自训练 Pipeline
- [ ] 自动化迭代训练流程：对弈 → 训练 → 评估 → 更新最优模型
- [ ] 支持模型持久化保存与加载
- [ ] 提供训练过程可视化（胜率曲线、loss 曲线）

---

## ⚠️ 当前局限与近期改进方向

尽管当前 AI 对普通玩家已有一定挑战性，但仍存在明显局限，计划在后续版本中解决：

1. **搜索深度固定** – 仅 2 层搜索，无法看到更长的连续冲刺（如 VCF）。  
   *改进：实现 Alpha‑Beta 剪枝，在合理时间内达到 4‑6 层深度。*

2. **手工设定的评分权重** – 棋形分值均为人工经验值，未必最优。  
   *改进：用遗传算法等优化方法自动寻找更优权重。*

3. **棋形模式有限** – 当前仅识别连续线型，缺少跳活三、跳冲四、双威胁等形状。  
   *改进：扩展模式库，提升局面判断精度。*

4. **无开局知识** – AI 开局阶段完全依赖搜索，缺乏定式。  
   *改进：可添加小型开局库，或通过自对弈数据学习开局。*

---

## 🤝 贡献指南

欢迎提交 Issue 与 Pull Request！如果你对以下方向感兴趣，尤其欢迎参与：
- 优化 AI 评分权重或增加更丰富的棋形模式
- 实现更多难度的 AI（如基于 MCTS 的 AI）
- 实现更优雅的控制台 UI（清屏、棋子符号美化）
- 增加悔棋、保存棋谱、回放功能
- 实现标准专业规则（黑棋禁手、三手交换、五手两打）
- 为 AI 模块编写单元测试

---

**Enjoy the game! 🎲**