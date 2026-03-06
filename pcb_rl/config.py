"""
PCB RL Configuration File
STM32 Crystal Layout and Routing Optimization
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class BoardConfig:
    """PCB Board Configuration"""
    width: float = 60.0      # mm
    height: float = 50.0     # mm
    resolution: float = 0.1   # mm per grid cell
    margin: float = 1.0      # board edge margin
    
    @property
    def grid_width(self) -> int:
        return int(self.width / self.resolution)
    
    @property
    def grid_height(self) -> int:
        return int(self.height / self.resolution)


@dataclass
class ComponentConfig:
    """Component Configuration"""
    # MCU (U1) - Fixed position
    mcu_ref: str = "U1"
    mcu_pos: Tuple[float, float] = (30.0, 25.0)  # mm
    mcu_size: Tuple[float, float] = (7.0, 7.0)   # mm
    
    # Crystal (Y1)
    crystal_ref: str = "Y1"
    crystal_size: Tuple[float, float] = (3.2, 2.5)  # mm
    
    # Load Capacitors (C1, C2)
    cap_refs: List[str] = field(default_factory=lambda: ["C1", "C2"])
    cap_size: Tuple[float, float] = (1.0, 0.5)  # mm (0402)


@dataclass
class NetConfig:
    """Network Configuration"""
    osc_in: Dict[str, List[Tuple[str, int]]] = field(default_factory=lambda: {
        "pins": [("U1", 5), ("Y1", 1), ("C1", 1)]
    })
    osc_out: Dict[str, List[Tuple[str, int]]] = field(default_factory=lambda: {
        "pins": [("U1", 6), ("Y1", 3), ("C2", 1)]
    })
    
    @property
    def nets(self) -> List[str]:
        return ["OSC_IN", "OSC_OUT"]


@dataclass
class DRCConfig:
    """Design Rule Check Configuration"""
    min_track_width: float = 0.2       # mm
    min_clearance: float = 0.2          # mm
    min_crystal_to_mcu: float = 0.5     # mm (reduced for simpler learning)
    min_cap_to_crystal: float = 0.3     # mm
    min_track_to_component: float = 0.2 # mm
    crystal_under禁止: float = 0.3       # mm (crystal underside forbidden zone)
    
    @property
    def min_clearance_cells(self) -> int:
        return int(self.min_clearance / 0.1)


@dataclass
class RewardConfig:
    """Reward Function Configuration"""
    r_completion: float = 100.0
    r_drc_violation: float = -5.0
    r_overlap: float = -20.0
    r_length: float = 0.0
    r_via: float = -10.0
    r_angle: float = 0.0
    r_symmetry: float = -0.5
    r_step: float = 0.0  # No step reward
    r_reach_target: float = 50.0  # Large reward for reaching target


@dataclass
class TrainingConfig:
    """Training Configuration"""
    total_timesteps: int = 100000
    eval_freq: int = 5000
    save_freq: int = 10000
    max_steps_per_episode: int = 1000
    n_envs: int = 4
    
    # PPO hyperparameters
    learning_rate: float = 3e-4
    n_steps: int = 2048
    batch_size: int = 64
    n_epochs: int = 10
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5


@dataclass
class ActionConfig:
    """Action Space Configuration"""
    # Direction mappings (dx, dy)
    directions: Dict[int, Tuple[int, int]] = field(default_factory=lambda: {
        0: (0, 1),    # N - North
        1: (0, -1),   # S - South
        2: (1, 0),    # E - East
        3: (-1, 0),   # W - West
        4: (1, 1),    # NE - North East
        5: (-1, 1),   # NW - North West
        6: (1, -1),   # SE - South East
        7: (-1, -1),  # SW - South West
        8: (0, 0),    # STOP
    })
    
    direction_names: Dict[int, str] = field(default_factory=lambda: {
        0: "N", 1: "S", 2: "E", 3: "W",
        4: "NE", 5: "NW", 6: "SE", 7: "SW", 8: "STOP"
    })
    
    @property
    def n_actions(self) -> int:
        return len(self.directions)


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

DIRECTION_NAMES = {
    0: "N", 1: "S", 2: "E", 3: "W",
    4: "NE", 5: "NW", 6: "SE", 7: "SW", 8: "STOP"
}


# Grid channel indices
CH_COMPONENT = 0  # Component occupied
CH_TRACK = 1      # Track occupied
CH_DRC = 2        # DRC forbidden


# Global config instances
BOARD = BoardConfig()
COMPONENT = ComponentConfig()
NET = NetConfig()
DRC = DRCConfig()
REWARD = RewardConfig()
TRAINING = TrainingConfig()
ACTION = ActionConfig()
