**中文README附在英文README后面，供中文用户参考。英文README是主版本，中文README会定期同步更新。**
# 🎯 Gomoku – Python Implementation

A pure Python implementation of the classic Gomoku (Five in a Row) board game. No third‑party libraries required. The game supports customizable board sizes, two‑player mode, and includes a built‑in heuristic AI opponent. The project is structured to allow future extensions toward a self‑training reinforcement learning AI.

---

## ✨ Current Features

- ✅ Pure Python – zero external dependencies
- ✅ Customizable board size (default 15×15)
- ✅ Clean console board display with row/column labels
- ✅ Fast win detection based on the last move only (O(1) complexity)
- ✅ Robust input validation and error messages
- ✅ Draw detection (when the board is full)
- ✅ **Human vs AI mode**: built‑in greedy scoring AI with basic offensive and defensive awareness

---

## 🚀 Quick Start

### Run the Game

```bash
python main.py
```

### Game Mode Selection

Upon starting, you can choose:
- **Two‑Player Mode**: two human players take turns.
- **Human vs AI Mode**: play against the AI and choose whether you want to play first (Player 1) or second (Player 2).

### Rules

- Player 1 uses **1**, Player 2 uses **2**
- Players take turns entering coordinates in the format: `row column` (both starting from 1)
- The first player to align five pieces horizontally, vertically, or diagonally wins

### Example Game (Human vs AI)

```
Welcome to Gomoku!
Choose the size of the board (default is 15):
15
Do you want to play against the AI? (y/n):
y
Do you want to be Player 1 or Player 2? (Enter 1 or 2):
1
  1  2  3  4  5 ...
1  0  0  0  0  0 ...
...
Player 1's turn. Enter row and column (1-15):
8 8
AI Player 2's turn.
AI places at 8 9
...
```

---

## 📁 Project Structure

```
.
├── main.py            # Main program, contains Board, normalAIplayer, and game loop
└── README.md          # Project documentation
```

---

## 🔧 Core Classes

### `Board(size=15)`

| Method                               | Description                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `place(player, [row, col])`          | Places a piece at the given position. Returns `True` if successful. Indices are 0‑based.   |
| `check_win(player, [row, col])`      | Checks whether the specified player has won after placing a piece at `[row, col]`.         |
| `print_board()`                      | Prints the current board state with row and column labels.                                  |

### `normalAIplayer`

A simple greedy AI that evaluates the board by scanning lines for predefined patterns (e.g., open two, open three, open four) and assigns a score to each empty cell. It then chooses the move with the highest combined offensive and defensive score.

| Method                 | Description                                                                    |
| ---------------------- | ------------------------------------------------------------------------------ |
| `make_move()`          | Executes one AI move and returns the 0‑based coordinates `[row, col]` played. |
| `get_best_move()`      | Iterates over all empty cells and returns the position with the highest score.  |
| `evaluate_board()`     | Evaluates the total score of the current board from a given player's perspective. |

---

## 🧠 Future Roadmap (Towards a Self‑Training Gomoku AI)

The long‑term goal is to build a Gomoku AI capable of **self‑play and self‑improvement** using reinforcement learning.

### 📌 Phase 1: Heuristic AI Foundation ✅
- [x] Board evaluation via pattern recognition
- [x] Greedy AI opponent based on scoring
- [x] Human vs AI gameplay

### 📌 Phase 2: Deep Reinforcement Learning (AlphaZero Style)
- [ ] Build a residual neural network (policy + value heads) using PyTorch
- [ ] Implement Monte Carlo Tree Search (MCTS)
- [ ] Multi‑channel board state encoding

### 📌 Phase 3: Self‑Play and Data Generation
- [ ] Self‑play data generator
- [ ] Replay buffer implementation
- [ ] Training loop with policy loss and value loss

### 📌 Phase 4: Full Self‑Training Pipeline
- [ ] Automated iteration: self‑play → training → evaluation → model update
- [ ] Model checkpoint saving and loading
- [ ] Training visualization (win rate curves, loss curves)

---

## 🤝 Contributing

Issues and Pull Requests are welcome! Areas where contributions are especially appreciated:

- Improving AI scoring weights or adding more sophisticated patterns (e.g., jump‑three, jump‑four)
- Enhancing console UI (screen clearing, prettier piece symbols)
- Adding undo, game saving, and replay functionality
- Implementing standard professional rules (black forbidden moves, swap opening, etc.)
- Writing unit tests for the AI module

---

**Enjoy the game! 🎲**



# 🎯 Gomoku (五子棋) – Python 实现

一个纯 Python 实现的五子棋游戏，无需任何第三方库。支持自定义棋盘大小、双人对战，并内置一个基于棋形评分的简易 AI 对手。项目已为后续强化学习扩展预留接口。

---

## ✨ 当前功能

- ✅ 纯 Python 实现，零外部依赖
- ✅ 可自定义棋盘尺寸（默认 15×15）
- ✅ 清晰的控制台棋盘显示（带行列号）
- ✅ 基于最后落子位置的快速赢棋检测（O(1) 复杂度）
- ✅ 完善的输入校验与错误提示
- ✅ 平局检测（棋盘下满）
- ✅ **人机对战模式**：内置贪心评分 AI，具备基础攻防能力

---

## 🚀 快速开始

### 运行游戏

```bash
python main.py
```

### 游戏模式选择

启动后可选择：
- **双人对战**：两名人类玩家轮流落子。
- **人机对战**：选择与 AI 对战，并可指定自己执先手（玩家1）或后手（玩家2）。

### 游戏规则

- 玩家 1 执 **1**，玩家 2 执 **2**
- 轮流输入落子坐标，格式：`行 列`（行列均从 1 开始计数）
- 率先在横、竖、斜任一方向连成五子者获胜

### 示例对局（人机对战）

```
Welcome to Gomoku!
Choose the size of the board (default is 15):
15
Do you want to play against the AI? (y/n):
y
Do you want to be Player 1 or Player 2? (Enter 1 or 2):
1
  1  2  3  4  5 ...
1  0  0  0  0  0 ...
...
Player 1's turn. Enter row and column (1-15):
8 8
AI Player 2's turn.
AI places at 8 9
...
```

---

## 📁 项目结构

```
.
├── main.py            # 主程序，包含 Board、normalAIplayer 及游戏循环
└── README.md          # 项目说明文档
```

---

## 🔧 核心类说明

### `Board(size=15)`

| 方法                                 | 描述                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `place(player, [row, col])`          | 在指定位置落子，返回是否成功。行列索引从 0 开始。                            |
| `check_win(player, [row, col])`      | 检测指定玩家在最新落子后是否获胜（仅检查落子点四个方向）。                    |
| `print_board()`                      | 在控制台打印当前棋盘状态（带行列号）。                                        |

### `normalAIplayer`

基于贪心算法的简易 AI，通过评估每条线上的棋形模式（活二、活三、活四等）为每个空位打分，选择攻防综合分最高的位置落子。

| 方法                   | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `make_move()`          | 执行一步 AI 落子，返回落子的 0-based 坐标 `[row, col]`。      |
| `get_best_move()`      | 遍历所有空位，返回评分最高的位置坐标。                         |
| `evaluate_board()`     | 评估当前棋盘对指定玩家的总得分。                               |

---

## 🧠 未来扩展路线（自训练五子棋 AI）

本项目的长期目标是实现一个能够**自我对弈、自我训练**的强化学习五子棋 AI。

### 📌 第一阶段：启发式 AI 基础 ✅
- [x] 实现棋盘局面评分函数（连子模式识别）
- [x] 基于贪心算法的简易 AI 对手
- [x] 支持人机对战模式

### 📌 第二阶段：深度强化学习（AlphaZero 风格）
- [ ] 使用 PyTorch 构建残差神经网络（策略网络 + 价值网络）
- [ ] 实现蒙特卡洛树搜索（MCTS）
- [ ] 完成棋盘状态的多通道编码

### 📌 第三阶段：自我对弈与数据生成
- [ ] 实现模型自我对弈数据生成器
- [ ] 构建经验回放池（Replay Buffer）
- [ ] 编写训练循环（策略损失 + 价值损失）

### 📌 第四阶段：完整自训练 Pipeline
- [ ] 自动化迭代训练流程：对弈 → 训练 → 评估 → 更新最优模型
- [ ] 支持模型持久化保存与加载
- [ ] 提供训练过程可视化（胜率曲线、loss 曲线）

---

## 🤝 贡献指南

欢迎提交 Issue 与 Pull Request！如果你对以下方向感兴趣，尤其欢迎参与：
- 优化 AI 评分权重或增加更丰富的棋形模式（如跳活三、跳冲四）
- 实现更优雅的控制台 UI（清屏、棋子符号美化）
- 增加悔棋、保存棋谱、回放功能
- 实现标准专业规则（黑棋禁手、三手交换、五手两打）
- 为 AI 模块编写单元测试

---

**Enjoy the game! 🎲**
