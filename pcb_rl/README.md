# STM32 晶振布局与走线强化学习优化方案

## 1. 问题概述

### 1.1 目标

使用强化学习（PPO 算法）优化 STM32 最小系统板中晶振（Y1）及相关电容（C1、C2）的布局和走线，满足以下要求：

- 走线不重叠
- 不覆盖元件
- 走线方向满足 PCB 规范（45°/90° 转弯）
- 最小间距 0.2mm
- 晶振下方禁放其他走线/铜皮

### 1.2 目标网络

```
OSC_IN:  U1(Pin5) ↔ Y1(Pin1) ↔ C1(Pin1)
OSC_OUT: U1(Pin6) ↔ Y1(Pin3) ↔ C2(Pin2)
```

### 1.3 性能指标

| 指标 | 当前方案 | RL 优化目标 |
|------|---------|------------|
| 走线长度 | ~15mm | <12mm |
| 走线对称性 | 有偏差 | <0.5mm 差 |
| 过孔数量 | 2个 | 0-1个 |
| DRC通过率 | 基线 | 100% |

---

## 2. 占用栅格地图设计

### 2.1 地图规格

```
板子尺寸: 60mm × 50mm
分辨率:   0.1mm / 格
网格数:   600 × 500
```

### 2.2 栅格通道设计

占用地图采用 **3 通道**设计：

| 通道 | 名称 | 描述 | 值范围 |
|------|------|------|--------|
| 通道0 | `OCCUPIED_BY_COMP` | 元件占用区域 | 0=空, 1=元件 |
| 通道1 | `OCCUPIED_BY_TRACK` | 走线占用区域 | 0=空, 1=走线 |
| 通道2 | `DRC_FORBIDDEN` | DRC 禁区域 | 0=可走, 1=禁止 |

### 2.3 占用掩码构建

```python
# 元件占用区域 (通道0)
# 每个元件根据其尺寸计算占用网格，扩展 0.2mm 边距
grid[0, x_min:x_max, y_min:y_max] = 1

# DRC 禁区域 (通道2)
# - 晶振正下方区域
# - 板边 1mm 范围内
# - 高速信号隔离区
grid[2, :, :] = 1  # 在禁区域设置
```

### 2.4 间距约束实现

```python
# 走线与元件的最小间距: 0.2mm = 2 格
# 在元件占用区域外扩展 2 格作为禁区域
component_extended = expand_mask(grid[0], padding=2)
grid[2] |= component_extended

# 走线之间的最小间距: 0.2mm = 2 格
# 每次放置走线后，扩展走线掩码
track_extended = expand_mask(grid[1], padding=2)
```

---

## 3. 状态空间设计

### 3.1 状态向量

```
State = {
    "grid": (3, 600, 500),       # 3通道占用地图
    "net_mask": (600, 500),     # 当前网络路径掩码
    "current_pos": (2,),        # 当前走线头位置 (x, y)
    "target_pos": (2,),         # 目标焊盘位置 (x, y)
    "features": (N, 6)          # 元件特征
}
```

### 3.2 元件特征

```python
Feature = [x, y, rotation, type, pin_count, net_id]

# type 编码:
# 0 = MCU (U1)
# 1 = 晶振 (Y1)
# 2 = 电容 (C1, C2)
# 3 = 其他
```

### 3.3 状态归一化

```python
# 位置归一化到 [0, 1]
x_norm = x / BOARD_WIDTH   # 60mm
y_norm = y / BOARD_HEIGHT  # 50mm

# 占用地图值归一化到 [0, 1]
grid_norm = grid.astype(np.float32) / 1.0
```

---

## 4. 动作空间设计

### 4.1 分层动作策略

采用 **两阶段** 动作设计：

```
阶段1: 元件放置
  └── 动作: 选择 (Y1, C1, C2) 的位置和旋转

阶段2: 走线规划
  └── 动作: 走线方向序列
```

### 4.2 走线方向（符合 PCB 规范）

```
方向集合: 8方向 + STOP
├── N:  北 (0, +1)
├── S:  南 (0, -1)  
├── E:  东 (+1, 0)
├── W:  西 (-1, 0)
├── NE: 东北 (+1, +1)
├── NW: 西北 (-1, +1)
├── SE: 东南 (+1, -1)
├── SW: 西南 (-1, -1)
└── STOP: 停止 (结束当前网络走线)
```

### 4.3 动作编码

```python
# 离散动作编码 (0-8)
ACTION_MAP = {
    0: (0, 1),    # N
    1: (0, -1),   # S
    2: (1, 0),    # E
    3: (-1, 0),   # W
    4: (1, 1),    # NE
    5: (-1, 1),   # NW
    6: (1, -1),   # SE
    7: (-1, -1),  # SW
    8: (0, 0),    # STOP
}

# 每步移动距离: 1 格 = 0.1mm
STEP_SIZE = 1
```

---

## 5. 奖励函数设计

### 5.1 奖励组成

```
R_total = R_completion + α*R_drc + β*R_length + γ*R_via + δ*R_overlap + ε*R_angle + ζ*R_symmetry
```

### 5.2 各奖励项

| 奖励项 | 值 | 描述 |
|--------|-----|------|
| `R_completion` | +100 | 完成所有网络连接 |
| `R_drc` | -50 | 进入 DRC 禁区域 |
| `R_overlap` | -100 | 走线重叠（硬约束） |
| `R_length` | -0.1 × 长度(mm) | 走线长度惩罚 |
| `R_via` | -10 | 每个过孔惩罚 |
| `R_angle` | -20 | 非 45°/90° 转弯 |
| `R_symmetry` | -0.5 × 长度差 | OSC_IN 与 OSC_OUT 长度差异 |
| `R_step` | -0.01 | 每步探索小惩罚 |

### 5.3 奖励代码实现

```python
def compute_reward(self, action, state, next_state, done):
    reward = 0.0
    
    # 1. 完成奖励
    if done and self.all_nets_connected():
        reward += 100.0
    
    # 2. DRC 违规惩罚
    if self.check_drc_violation(next_state):
        reward -= 50.0
    
    # 3. 重叠惩罚（硬约束）
    if self.check_overlap(next_state):
        reward -= 100.0
        return reward  # 硬约束，立即返回
    
    # 4. 长度惩罚
    track_length = self.compute_track_length(next_state)
    reward -= 0.1 * track_length
    
    # 5. 过孔惩罚
    via_count = self.count_vias(next_state)
    reward -= 10.0 * via_count
    
    # 6. 转弯角度惩罚
    if not self.is_valid_angle(action):
        reward -= 20.0
    
    # 7. 对称性奖励
    length_in = self.get_net_length("OSC_IN")
    length_out = self.get_net_length("OSC_OUT")
    reward -= 0.5 * abs(length_in - length_out)
    
    return reward
```

### 5.4 权重参数

```python
WEIGHTS = {
    'alpha': 1.0,   # DRC 权重
    'beta': 0.1,    # 长度权重
    'gamma': 2.0,   # 过孔权重
    'delta': 1.0,   # 重叠权重
    'epsilon': 1.0,  # 角度权重
    'zeta': 1.0,    # 对称性权重
}
```

---

## 6. 碰撞检测流程

### 6.1 检测步骤

```
每次动作执行后:

Step 1: 计算新走线覆盖的栅格
        new_cells = compute_path_cells(current_pos, action)

Step 2: 检查元件占用冲突
        if grid[0, new_cells] == 1:
            collision = True

Step 3: 检查走线重叠
        if grid[1, new_cells] == 1:
            overlap = True

Step 4: 检查 DRC 禁区域
        if grid[2, new_cells] == 1:
            drc_violation = True

Step 5: 检查转弯角度
        if not is_45_or_90_degree(prev_direction, current_direction):
            angle_violation = True

Step 6: 检查间距
        if min_distance_to_track(new_cells, grid[1]) < 2:
            spacing_violation = True
```

### 6.2 间距计算

```python
def check_min_spacing(self, new_cells, min_distance=2):
    """检查与已有走线的最小间距"""
    # 扩展已有走线掩码
    track_mask = expand_mask(self.grid[1], padding=min_distance)
    
    # 检查新走线是否进入扩展区域
    for cell in new_cells:
        if track_mask[cell[0], cell[1]] == 1:
            return False  # 间距不足
    
    return True
```

---

## 7. 环境接口定义

### 7.1 Gymnasium 接口

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CrystalRLEnv(gym.Env):
    metadata = {'render_modes': ['human']}
    
    def __init__(self, config=None):
        super().__init__()
        
        # 配置参数
        self.board_width = 60.0   # mm
        self.board_height = 50.0  # mm
        self.resolution = 0.1     # mm/格
        self.grid_width = int(self.board_width / self.resolution)
        self.grid_height = int(self.board_height / self.resolution)
        
        # 动作空间: 9 个离散动作 (8方向 + STOP)
        self.action_space = spaces.Discrete(9)
        
        # 观察空间
        self.observation_space = spaces.Dict({
            'grid': spaces.Box(
                low=0, high=1,
                shape=(3, self.grid_height, self.grid_width),
                dtype=np.float32
            ),
            'net_mask': spaces.Box(
                low=0, high=1,
                shape=(self.grid_height, self.grid_width),
                dtype=np.float32
            ),
            'current_pos': spaces.Box(
                low=0, high=1,
                shape=(2,),
                dtype=np.float32
            ),
            'target_pos': spaces.Box(
                low=0, high=1,
                shape=(2,),
                dtype=np.float32
            ),
        })
        
        # 初始化
        self.grid = None
        self.current_net = None
        self.step_count = 0
        self.max_steps = 1000
        
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 初始化占用地图
        self.grid = np.zeros((3, self.grid_height, self.grid_width), dtype=np.float32)
        
        # 放置 MCU (固定位置)
        self._place_mcu()
        
        # 初始化目标网络
        self.current_net = "OSC_IN"
        self.target_pos = self._get_target_position()
        
        # 重置步数
        self.step_count = 0
        
        return self._get_obs(), {}
    
    def step(self, action):
        """执行动作"""
        self.step_count += 1
        
        # 解析动作
        if action == 8:  # STOP
            done = True
            reward = 0
        else:
            # 移动走线
            dx, dy = ACTION_MAP[action]
            new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
            
            # 碰撞检测
            if self._check_collision(new_pos):
                reward = -100  # 重叠惩罚（硬约束）
                done = True
            elif self._check_drc_violation(new_pos):
                reward = -50   # DRC 违规
                done = True
            elif self._reached_target(new_pos):
                reward = 50    # 到达目标
                done = True
            else:
                # 正常移动
                self._update_grid(new_pos)
                reward = -0.01  # 探索惩罚
        
        # 检查是否超时
        if self.step_count >= self.max_steps:
            done = True
        
        obs = self._get_obs()
        info = {'step': self.step_count}
        
        return obs, reward, done, False, info
    
    def _check_collision(self, pos):
        """检查碰撞"""
        x, y = int(pos[0]), int(pos[1])
        
        # 边界检查
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return True
        
        # 元件占用检查
        if self.grid[0, y, x] == 1:
            return True
        
        # 走线重叠检查
        if self.grid[1, y, x] == 1:
            return True
        
        return False
    
    def _check_drc_violation(self, pos):
        """检查 DRC 违规"""
        x, y = int(pos[0]), int(pos[1])
        return self.grid[2, y, x] == 1
    
    def _get_obs(self):
        """获取观察"""
        return {
            'grid': self.grid,
            'net_mask': self.net_mask,
            'current_pos': np.array(self.current_pos) / [self.board_width, self.board_height],
            'target_pos': np.array(self.target_pos) / [self.board_width, self.board_height],
        }
```

---

## 8. PPO Agent 设计

### 8.1 网络架构

```
┌─────────────────────────────────────────┐
│           观察输入 (Observation)          │
├─────────────────┬───────────────────────┤
│   Grid (3×600×500)  │  Positions (4,)    │
└────────┬────────┴──────────┬────────────┘
         │                   │
         ▼                   ▼
┌─────────────────┐   ┌───────────────┐
│  CNN Encoder    │   │  MLP Encoder  │
│  (3 → 256)      │   │  (4 → 64)     │
└────────┬────────┘   └───────┬───────┘
         │                   │
         └────────┬──────────┘
                  ▼
         ┌─────────────────┐
         │  Concatenate    │
         │  (320,)         │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │   MLP Block     │
         │  (320 → 256)   │
         └────────┬────────┘
                  │
      ┌──────────┴──────────┐
      ▼                     ▼
┌─────────────┐      ┌─────────────┐
│ Policy Head │      │ Value Head  │
│ (256 → 9)   │      │ (256 → 1)   │
└─────────────┘      └─────────────┘
```

### 8.2 PPO 实现

```python
import torch
import torch.nn as nn
from torch.distributions import Categorical
from stable_baselines3 import PPO

class PPOCrystalAgent:
    def __init__(self, env_config):
        # 使用 Stable-Baselines3 的 PPO
        self.model = PPO(
            "MultiInputPolicy",
            env=env_config,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            verbose=1,
            tensorboard_log="./logs/",
            device="cuda"  # 或 "cpu"
        )
    
    def train(self, total_timesteps=100000):
        """训练模型"""
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=TensorboardCallback(),
            progress_bar=True
        )
    
    def save(self, path):
        """保存模型"""
        self.model.save(path)
    
    def load(self, path):
        """加载模型"""
        self.model = PPO.load(path)
    
    def predict(self, obs, deterministic=True):
        """预测动作"""
        action, _ = self.model.predict(obs, deterministic=deterministic)
        return action
```

---

## 9. 训练配置

### 9.1 超参数

```python
TRAINING_CONFIG = {
    # PPO 超参数
    'learning_rate': 3e-4,
    'n_steps': 2048,
    'batch_size': 64,
    'n_epochs': 10,
    'gamma': 0.99,           # 折扣因子
    'gae_lambda': 0.95,      # GAE 参数
    'clip_range': 0.2,      # PPO 裁剪范围
    'ent_coef': 0.01,       # 熵系数 (探索)
    
    # 训练参数
    'total_timesteps': 100000,
    'eval_freq': 5000,
    'save_freq': 10000,
    
    # 环境参数
    'max_steps': 1000,      # 每个 episode 最大步数
    'n_envs': 4,            # 并行环境数
}
```

### 9.2 奖励归一化

```python
# 使用 RunningMeanStd 归一化奖励
class NormalizedReward(gym.Wrapper):
    def __init__(self, env, gamma=0.99):
        super().__init__(env)
        self.gamma = gamma
        self.returns = 0
        self.count = 0
    
    def step(self, action):
        obs, reward, done, truncated, info = self.env.step(action)
        
        self.returns = reward + self.gamma * self.returns
        self.count += 1
        
        # 归一化
        if self.count > 100:
            mean = self.returns / self.count
            reward = reward - mean
        
        return obs, reward, done, truncated, info
```

---

## 10. 实施步骤

### 10.1 文件结构

```
pcb_rl/
├── crystal_env.py          # 晶振 RL 环境
├── ppo_agent.py           # PPO Agent 实现
├── train.py               # 训练脚本
├── evaluate.py           # 评估脚本
├── config.py              # 配置文件
├── utils/
│   ├── grid_utils.py      # 栅格工具
│   ├── drc_checker.py     # DRC 检查器
│   └── __init__.py
├── models/                # 保存的模型
│   └── crystal_ppo.zip
└── logs/                  # TensorBoard 日志
```

### 10.2 实施顺序

```
Step 1: 环境实现 (crystal_env.py)
  - 初始化占用栅格地图
  - 实现 reset() 和 step()
  - 实现碰撞检测
  - 实现奖励计算

Step 2: Agent 实现 (ppo_agent.py)
  - 定义网络架构
  - 实现 PPO 训练循环

Step 3: 训练 (train.py)
  - 配置超参数
  - 启动训练
  - 监控收敛

Step 4: 评估 (evaluate.py)
  - 加载最优模型
  - 生成布局
  - 可视化结果

Step 5: 集成 (integration)
  - 将 RL 结果应用到原 PCB 脚本
  - 生成最终 PCB 文件
```

---

## 11. 预期结果

### 11.1 训练收敛

| 阶段 | Episode | 平均奖励 | 成功率 |
|------|---------|---------|-------|
| 初期 | 0-1000 | -50 | 10% |
| 中期 | 1000-5000 | +20 | 50% |
| 后期 | 5000+ | +80 | 90% |

### 11.2 优化效果

| 指标 | 优化前 | 优化后 |
|------|-------|-------|
| 总走线长度 | ~15mm | <12mm |
| 长度对称差 | >1mm | <0.5mm |
| 过孔数量 | 2个 | 0-1个 |
| DRC 通过率 | ~80% | 100% |

---

## 12. 附录

### 12.1 依赖库

```bash
pip install gymnasium
pip install stable-baselines3
pip install torch torchvision
pip install numpy
pip install matplotlib
```

### 12.2 硬件要求

```
- GPU: NVIDIA GTX 1060+ (推荐)
- RAM: 8GB+
- 训练时间: ~2-4 小时
```

### 12.3 参考资料

- [Stable-Baselines3 文档](https://stable-baselines3.readthedocs.io/)
- [PPO 论文](https://arxiv.org/abs/1707.06347)
- [Gymnasium 文档](https://gymnasium.farama.org/)

---

*文档版本: 1.0*  
*最后更新: 2026-03-05*
