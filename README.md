# MiniGomoku 五子棋

这是一个纯 Python 的五子棋项目，当前版本已经完成一次较大的结构整理。现在的核心思路很明确：

- `board.py` 是规则唯一来源
- `AI/pattern.py` 统一维护棋形和染色体
- `AI/base.py` 统一玩家接口，后面可以直接接自我对弈和强化学习
- 现有 AI 保留，不新增新 AI 类型
- 训练、命令行、GUI、测试都已经按同一套接口对齐

详细改动说明见 [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)。

---

## 现在能做什么

- 命令行对战
- 图形界面对战
- 人机对战
- AI 对 AI 调试
- 遗传算法调参
- 基础回归测试

当前实现的是自由五子棋规则，连五及以上均算胜利；黑棋禁手、交换规则、开局库这些还没加。

---

## 快速开始

### 运行命令行版
```bash
python main.py
```

### 运行图形界面版
```bash
python gui.py
```

### 运行基础测试
```bash
python -m unittest discover -s tests
```

### 查看训练入口参数
```bash
python Training/run_tuning.py --help
```

---

## 命令行怎么玩

`main.py` 里会先让你输入棋盘大小，默认 `15`，有效范围是 `5` 到 `25`。

随后会进入对局模式选择：

- 输入 `n`：人人对战
- 输入 `y`：人机对战
- 输入 `test`：AI 对 AI 调试模式

如果选择人机对战，还会继续让你选：

- 自己执黑还是执白
- AI 类型
  - `1`：`HeuristicAIDepth`
  - `2`：`MCTS_AI`
- 若选启发式 AI，还可以设置搜索深度，并选择是否加载遗传算法优化后的权重文件

命令行里人类输入支持：

- `row col`
- `row,col`
- `row，col`

内部坐标全部是 `0-based`，界面显示时才会转成 `1-based`。

---

## 项目结构

```text
.
├── main.py
├── gui.py
├── board.py
├── human.py
├── AI/
│   ├── base.py
│   ├── pattern.py
│   ├── Heuristic_ai.py
│   ├── Heuristic_ai_depth.py
│   ├── Heuristic_ai_depth2.py
│   ├── MCTS_ai.py
│   └── MCTS_node.py
├── Training/
│   ├── config.py
│   ├── arena.py
│   ├── genetic.py
│   └── run_tuning.py
├── tests/
├── MODULE_TASK_PLAN.md
├── TECHNICAL_REPORT.md
└── README.md
```

---

## 核心模块

### `board.py`

现在它是棋盘规则和局面状态的唯一来源，负责：

- `apply_move(player, pos)`：合法落子
- `undo_move(pos=None)`：撤销落子
- `legal_moves()`：返回所有可落点
- `is_legal_move(pos)`：判断坐标是否合法
- `check_win(player, pos)`：判断是否获胜
- `clone()`：复制完整棋盘状态
- `create_key()`：生成稳定局面 key，方便缓存和回放
- `reset(size=None)`：重置棋盘

为了兼容旧代码，也保留了：

- `place()` -> `apply_move()`
- `remove()` -> `undo_move()`

它还会维护这些状态：

- `move_history`
- `last_move`
- `move_count`
- `current_player`
- `cnt_player`

### `human.py`

`Human` 负责命令行输入解析和校验：

- 同时支持空格和逗号分隔
- 非整数、越界、占用位置都会给出单独提示
- 校验通过后返回 `(row, col)`，内部使用 `0-based`

### `AI/base.py`

这是所有玩家对象的统一接口层，当前保留的方法有：

- `get_move()`
- `make_move()`
- `reset()`
- `set_board(board)`
- `observe_move(player, move)`
- `on_game_end(result)`

这些 hook 不是为了现在就做复杂逻辑，而是给以后自我对弈、回放记录、强化学习留接口。

### `AI/pattern.py`

这里是启发式评估的共享中枢，统一维护：

- 棋形字典
- 玩家 1 / 玩家 2 的镜像关系
- 默认分值
- 染色体边界
- 染色体合法性校验

当前染色体长度是 `10`，对应：

1. 活二
2. 跳二
3. 活三
4. 跳三
5. 活四
6. 五
7. 眠二
8. 眠三
9. 眠四
10. `defense_weight`

### `AI/Heuristic_ai.py`

这是最基础的贪心启发式 AI，适合作为 baseline 或对照组。

### `AI/Heuristic_ai_depth.py`

这是当前主力搜索 AI，核心特点是：

- 候选点剪枝
- Alpha-Beta 剪枝
- 静态搜索/静态延伸
- 立即赢棋检查
- 强制防守检查
- 统一引用 `AI/pattern.py`
- 支持可选 `weights` 染色体

它是现在命令行和 GUI 里默认最常用的启发式 AI。

### `AI/Heuristic_ai_depth2.py`

保留为参考版 2-ply 搜索，不走主流程。

### `AI/MCTS_node.py`

MCTS 节点现在保留了更完整的信息：

- `action`
- `player_to_move`
- `state_key`
- `prior`
- `depth`

这些字段是给后续 PUCT、策略网络、转置表留口子的。

### `AI/MCTS_ai.py`

这是当前的 MCTS 实现，特点是：

- 先查立即赢棋
- 再查必须防守的强威胁
- 树搜索时同步模拟盘
- rollout 使用随机模拟
- 空盘时候选点会回到中心

### `Training/`

训练相关内容已经统一放到 `Training/` 下：

- `config.py`：默认棋盘大小、基因边界、染色体和输出目录
- `arena.py`：无界面对局环境和适应度计算
- `genetic.py`：遗传算法主循环，支持多进程并行评估
- `run_tuning.py`：训练入口脚本

训练输出默认写到 `Training/output/`，通常会生成：

- `*_history.csv`
- `*_best_chrom.json`
- `*_summary.json`
- 兼容旧命名的 `best_chrom_depth_{depth}.json`

### `tests/`

目前有最基础的回归测试：

- `tests/test_board.py`
- `tests/test_pattern.py`
- `tests/test_human.py`

它们覆盖了落子、撤销、克隆、五连判断、棋形镜像、染色体校验和输入重试。

---

## 训练怎么用

遗传算法入口是：

```bash
python Training/run_tuning.py
```

常用参数有：

- `--pop-size`
- `--generations`
- `--num-games`
- `--depth`
- `--seed`
- `--output-dir`
- `--artifact-prefix`

训练时会调用 `Training/arena.py` 做对局评估，并在 `Training/genetic.py` 中用 `ProcessPoolExecutor` 并行计算适应度。

如果要加载训练出来的权重，启发式 AI 会优先读取：

```text
Training/output/best_chrom_depth_{depth}.json
```

---

## 这次重构后，后面好接什么

现在已经预留了这些接口：

- `Board.move_history`
- `Board.create_key()`
- `BaseAI.reset()`
- `BaseAI.observe_move()`
- `BaseAI.on_game_end()`
- `BaseAI.set_board()`
- `MCTSNode.state_key`
- `MCTSNode.prior`

所以后面如果要做：

- 自我对弈
- Replay Buffer
- 策略网络 / 价值网络
- 神经网络引导的 MCTS

可以直接接现有骨架，不用再重造底层。

---

## 已知限制

- 还没有加入黑棋禁手
- 还没有加入开局库
- `Heuristic_ai_depth2.py` 只是参考实现
- 目前的 MCTS 还是随机 rollout，不是神经网络版
- GUI 目前支持人机和人人对战，不是 AI 对 AI 主界面

---

## 文档索引

- [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)：详细技术报告，适合回看重构具体改了什么
- [MODULE_TASK_PLAN.md](MODULE_TASK_PLAN.md)：模块级执行清单，适合按步骤理解整个重构路线

