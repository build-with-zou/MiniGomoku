
**中文README附在英文README后面，供中文用户参考。英文README是主版本，中文README会定期同步更新。**
# 🎯 Gomoku – Python Implementation

A pure Python implementation of the classic Gomoku (Five in a Row) board game. No third‑party libraries required. The game supports customizable board sizes, two‑player mode, multiple built‑in AI opponents with different strategies, and a graphical user interface (GUI). The project is structured to allow future extensions toward a self‑training reinforcement learning AI.

---

## ✨ Current Features

- ✅ Pure Python – zero external dependencies
- ✅ Customizable board size (default 15×15)
- ✅ Clean console board display with row/column labels
- ✅ Fast win detection based on the last move only (O(1) complexity)
- ✅ Robust input validation and error messages
- ✅ Draw detection (when the board is full)
- ✅ **Multiple AI difficulties**:
  - `HeuristicAI` – greedy one‑step pattern scoring (fast)
  - `HeuristicAIDepth` – configurable depth minimax search with **alpha‑beta pruning** and incremental evaluation (depth 1–4)
- ✅ **Graphical User Interface (GUI)** using built‑in `tkinter` – click to play, with status bar and restart
- ✅ **Human vs AI**, **Human vs Human**, and **AI vs AI** (test mode) in command line, plus GUI versions of all modes
- ✅ **Unified player interface**: human and AI players are treated identically, making it easy to add new AI opponents
- ✅ Incremental board evaluation for fast move scoring (only affected lines recomputed)

---

## 🚀 Quick Start

### Run the Game

#### Command Line (original)
```bash
python main.py
```

#### GUI
```bash
python gui.py
```

### Game Mode Selection

**In command line:**
- **Two‑Player Mode**: two human players take turns.
- **Human vs AI Mode**: play against the AI, choose your side, and select the AI difficulty.
- **AI vs AI (Test)**: enter `test` when asked for game mode, then set depths for both AIs.

**In GUI:**
- A dialog asks for board size, whether to play against AI, your side, and AI difficulty.  
- Click on the board to place your piece; the AI responds automatically.

### Rules

- Player 1 uses **1** (Black), Player 2 uses **2** (White)
- Players take turns entering coordinates or clicking on the board (both starting from 1)
- The first player to align five pieces horizontally, vertically, or diagonally wins

---

## 📁 Project Structure

```
.
├── main.py                       # Command‑line program (game loop, user interaction)
├── gui.py                        # Graphical user interface (tkinter)
├── board.py                      # Board class (board state, move validation, win detection)
├── human.py                      # Human player class (console input)
├── AI/
│   ├── base.py                   # Abstract base class for all AI players
│   ├── Heuristic_ai.py           # Greedy one‑step heuristic AI
│   ├── Heuristic_ai_depth2.py    # (Legacy) 2‑ply minimax AI (kept for reference)
│   └── Heuristic_ai_depth.py     # Configurable‑depth minimax AI with alpha‑beta pruning
└── README.md                     # Project documentation
```

> *Note: All game‑specific logic (Board, players, AI) is cleanly separated into dedicated modules. The GUI is fully decoupled from the command‑line interface.*

---

## 🔧 Core Classes

### `Board(size=15)`

| Method                               | Description                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `place(player, [row, col])`          | Places a piece at the given position. Returns `True` if successful. Indices are 0‑based.   |
| `check_win(player, [row, col])`      | Checks whether the specified player has won after placing a piece at `[row, col]`.         |
| `is_empty()` / `is_full()`           | Returns whether the board is empty or full.                                                |
| `print_board()`                      | Prints the current board state with row and column labels.                                  |

### `BaseAI` (Abstract Base Class)

All AI and human players inherit from `BaseAI`, which defines the required interface:

| Method                 | Description                                                                    |
| ---------------------- | ------------------------------------------------------------------------------ |
| `get_move()`           | Returns a `(row, col)` tuple representing the AI's chosen move, or `None` if no moves are available. |
| `make_move()`          | Executes the move by calling `get_move()` and placing the piece on the board.   |

### `HeuristicAI(BaseAI)`

A fast greedy scoring AI that evaluates only the four lines passing through each candidate move. It balances offensive and defensive pattern scores (open two, open three, etc.) using a configurable weight.

### `HeuristicAIDepth(BaseAI)`

**The main AI for adjustable difficulty.**  
Uses a minimax search with **alpha‑beta pruning** and **candidate pruning** (only cells near existing stones). The search depth is configurable (default 3).  
To keep the search fast, it employs **incremental evaluation**: it maintains a total board score and updates it only along the four lines affected by a simulated move, avoiding full‑board scans during search. Immediate win/loss detection terminates the search early.  
Set `depth=1` for greedy strength, `depth=2` for basic tactics, `depth=3‑4` for stronger play (requires more CPU time at depth 4).

### `Human(BaseAI)`

Implements the same interface as AI players, obtaining moves from console input. In the GUI, human input is handled by mouse clicks, but the class is still used for console mode.

---

## 🧠 Future Roadmap (Towards a Self‑Training Gomoku AI)

### 📌 Phase 1: Heuristic AI Foundation ✅
- [x] Board evaluation via pattern recognition
- [x] Greedy one‑step AI opponent
- [x] Configurable‑depth minimax with alpha‑beta pruning
- [x] Incremental evaluation for speed
- [x] Human vs AI gameplay (console + GUI)
- [x] Modular player interface for easy AI swapping

### 📌 Phase 2: Stronger Search & Automatic Tuning
- [ ] Add quiescence search / better horizon‑effect handling
- [ ] Use genetic algorithms to automatically tune scoring weights and defense weight
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

1. **Hand‑tuned scoring weights** – Pattern scores and the defense weight are manually set and could be suboptimal.  
   *Plan: apply genetic algorithms to discover better weights.*
2. **Limited pattern set** – Only continuous lines are considered; jump‑three, jump‑four, and double‑threat patterns are missing.  
   *Plan: extend the pattern library for finer positional judgment.*
3. **Horizon effect** – Even with depth 4, the AI may push threats beyond the search horizon, leading to occasional mis‑evaluations.  
   *Plan: implement quiescence search or a more sensitive evaluation around potential wins.*
4. **No opening book** – The AI relies entirely on search from the first move.  
   *Plan: add a small opening book or use self‑play data to learn openings.*

---

## 🤝 Contributing

Issues and Pull Requests are welcome! Areas where contributions are especially appreciated:

- Improving AI scoring weights or adding more sophisticated patterns
- Implementing additional AI difficulty levels (e.g., MCTS‑based AI)
- Enhancing the GUI (better graphics, animations, undo button)
- Adding undo, game saving, and replay functionality
- Implementing standard professional rules (black forbidden moves, swap opening, etc.)
- Writing unit tests for the AI module

---

**Enjoy the game! 🎲**



# 🎯 Gomoku (五子棋) – Python 实现

一个纯 Python 实现的五子棋游戏，无需任何第三方库。支持自定义棋盘大小、双人对战、多种策略的 AI 对手以及图形用户界面（GUI）。项目已为后续强化学习扩展预留接口。

---

## ✨ 当前功能

- ✅ 纯 Python 实现，零外部依赖
- ✅ 可自定义棋盘尺寸（默认 15×15）
- ✅ 清晰的控制台棋盘显示（带行列号）
- ✅ 基于最后落子位置的快速赢棋检测（O(1) 复杂度）
- ✅ 完善的输入校验与错误提示
- ✅ 平局检测（棋盘下满）
- ✅ **多种 AI 难度**：
  - `HeuristicAI` – 贪心一步评分（快速）
  - `HeuristicAIDepth` – 可调深度的极小极大搜索，带 **Alpha‑Beta 剪枝** 和增量评估（深度 1‑4）
- ✅ **图形用户界面（GUI）**（基于内置 `tkinter`）– 点击落子，状态栏提示，支持重新开始
- ✅ 支持 **人机对战**、**人人对战** 以及 **AI 对 AI 测试**（命令行），GUI 也包含前两种模式
- ✅ **统一的玩家接口**：人类与 AI 被同等对待，易于增加新的 AI 对手
- ✅ 增量棋盘评估：每次只计算落子点相关线条的分数变化，大幅提高搜索速度

---

## 🚀 快速开始

### 运行游戏

#### 命令行模式
```bash
python main.py
```

#### 图形界面模式
```bash
python gui.py
```

### 游戏模式选择

**命令行下：**
- **双人对战**：两名人类玩家轮流落子。
- **人机对战**：选择与 AI 对战，指定自己执先手或后手，并选择 AI 难度。
- **AI 测试**：在问及游戏模式时输入 `test`，即可设置两名 AI 的搜索深度，观看 AI 对战。

**GUI 下：**
- 启动后会弹出对话框，依次设置棋盘大小、是否人机对战、你的棋子颜色、AI 搜索深度。  
- 点击棋盘交叉点落子，AI 会自动回应。

### 游戏规则

- 玩家 1 执 **1**（黑），玩家 2 执 **2**（白）
- 轮流输入落子坐标或点击棋盘（行、列均从 1 开始计数）
- 率先在横、竖、斜任一方向连成五子者获胜

---

## 📁 项目结构

```
.
├── main.py                       # 命令行主程序（游戏循环与用户交互）
├── gui.py                        # 图形用户界面（tkinter）
├── board.py                      # Board 类（棋盘状态、落子验证、胜负判断）
├── human.py                      # 人类玩家类（控制台输入）
├── AI/
│   ├── base.py                   # 所有 AI 的抽象基类
│   ├── Heuristic_ai.py           # 贪心一步启发式 AI
│   ├── Heuristic_ai_depth2.py    # （旧版）2层极小极大 AI（保留作为参考）
│   └── Heuristic_ai_depth.py     # 可调深度的极小极大 AI（带 Alpha‑Beta 剪枝）
└── README.md                     # 项目说明文档
```

> *注：游戏逻辑 (Board, players, AI) 完全分离，GUI 与命令行界面彼此独立。*

---

## 🔧 核心类说明

### `Board(size=15)`

| 方法                                 | 描述                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `place(player, [row, col])`          | 在指定位置落子，返回是否成功。行列索引从 0 开始。                            |
| `check_win(player, [row, col])`      | 检测指定玩家在最新落子后是否获胜（仅检查落子点四个方向）。                    |
| `is_empty()` / `is_full()`           | 返回棋盘是否为空或已满。                                                     |
| `print_board()`                      | 在控制台打印当前棋盘状态（带行列号）。                                        |

### `BaseAI` (抽象基类)

所有 AI 及人类玩家均继承自 `BaseAI`，它规定了必须实现的接口：

| 方法                   | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `get_move()`           | 返回 AI 选择的落子坐标 `(row, col)`，若无合法位置则返回 `None`。 |
| `make_move()`          | 调用 `get_move()` 并在棋盘上落子。                            |

### `HeuristicAI(BaseAI)`

贪心一步评分 AI，只评估候选落子点四个方向上的棋形模式（活二、活三、活四等），平衡攻防分数后选择综合分最高的位置。速度极快，但缺乏长远规划。

### `HeuristicAIDepth(BaseAI)`

**可调节难度的主要 AI。**  
采用带 **Alpha‑Beta 剪枝** 的极小极大搜索，并利用**候选点剪枝**（只搜索棋子周围空位）。搜索深度可通过 `depth` 参数设定（默认 3）。  
为保证搜索速度，使用了**增量评估**：维护一个全局总分，每次模拟落子仅更新受影响的四条线，叶子节点直接返回总分，无需全盘重新扫描。搜索中遇到连五会立即返回。  
设置 `depth=1` 可获得贪心强度，`depth=2` 获得基础战术，`depth=3‑4` 则更强（深度 4 时计算时间稍长）。

### `Human(BaseAI)`

实现了与 AI 相同的接口，通过控制台获取用户输入。在 GUI 中，人类输入由鼠标点击处理，但该类仍用于命令行模式。

---

## 🧠 未来扩展路线（自训练五子棋 AI）

### 📌 第一阶段：启发式 AI 基础 ✅
- [x] 实现棋盘局面评分函数（连子模式识别）
- [x] 贪心一步 AI 对手
- [x] 可调深度极小极大搜索，带 Alpha‑Beta 剪枝
- [x] 增量评估加速搜索
- [x] 支持人机对战（命令行 + GUI）
- [x] 模块化玩家接口，便于替换不同 AI

### 📌 第二阶段：更强的搜索与自动调参
- [ ] 添加静态搜索以缓解地平线效应
- [ ] 使用遗传算法自动优化评分权重及防守权重
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

1. **手工设定的评分权重** – 棋形分值和防守权重均为人工设定，可能并非最优。  
   *改进：用遗传算法自动寻找更优权重。*
2. **棋形模式有限** – 仅识别连续线型，缺少跳活三、跳冲四、双威胁等形状。  
   *改进：扩展模式库，提升局面判断精度。*
3. **地平线效应** – 即使深度为 4，AI 仍可能将威胁推到搜索范围之外，导致误判。  
   *改进：实现静态搜索或增强对潜在杀棋的敏感度。*
4. **无开局知识** – AI 开局完全依赖搜索，缺乏定式。  
   *改进：可添加小型开局库，或通过自对弈数据学习开局。*

---

## 🤝 贡献指南

欢迎提交 Issue 与 Pull Request！如果你对以下方向感兴趣，尤其欢迎参与：
- 优化 AI 评分权重或增加更丰富的棋形模式
- 实现更多难度的 AI（如基于 MCTS 的 AI）
- 增强 GUI（更美观的界面、动画、悔棋按钮）
- 增加悔棋、保存棋谱、回放功能
- 实现标准专业规则（黑棋禁手、三手交换、五手两打）
- 为 AI 模块编写单元测试

---

**Enjoy the game! 🎲**
