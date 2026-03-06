"""
Crystal RL Environment for STM32 PCB Layout Optimization
Uses Gymnasium interface
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, List, Optional, Any

from config import (
    BOARD, COMPONENT, NET, DRC, REWARD, ACTION,
    ACTION_MAP, DIRECTION_NAMES, CH_COMPONENT, CH_TRACK, CH_DRC
)
from utils.grid_utils import (
    mm_to_grid, grid_to_mm,
    create_component_mask, create_rectangular_mask,
    expand_mask, create_track_mask, get_line_cells,
    check_path_collision, compute_track_length,
    validate_angle, get_bresenham_line,
    create_crystal_forbidden_zone, create_board_edge_mask
)

class Component:
    """Component data structure"""
    def __init__(self, ref: str, pos: Tuple[float, float], 
                 size: Tuple[float, float], rotation: float = 0):
        self.ref = ref
        self.pos = pos  # (x, y) in mm
        self.size = size  # (width, height) in mm
        self.rotation = rotation
        
    def to_grid(self) -> Tuple[int, int]:
        return (mm_to_grid(self.pos[0]), mm_to_grid(self.pos[1]))
    

class CrystalRLEnv(gym.Env):
    """
    Reinforcement Learning Environment for Crystal Layout and Routing
    
    This environment optimizes the placement of crystal (Y1) and load 
    capacitors (C1, C2) and their routing to the MCU (U1).
    """
    
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, config: Dict = None):
        super().__init__()
        
        self.config = config or {}
        
        # Board parameters
        self.board_width = BOARD.width
        self.board_height = BOARD.height
        self.resolution = BOARD.resolution
        self.grid_width = BOARD.grid_width
        self.grid_height = BOARD.grid_height
        
        # Component parameters
        self.mcu_pos = COMPONENT.mcu_pos
        self.mcu_size = COMPONENT.mcu_size
        self.crystal_size = COMPONENT.crystal_size
        self.cap_size = COMPONENT.cap_size
        
        # DRC parameters
        self.min_clearance_cells = DRC.min_clearance_cells
        self.min_crystal_to_mcu = DRC.min_crystal_to_mcu
        self.crystal_forbidden = DRC.crystal_under禁止
        
        # Action space: 9 discrete actions (8 directions + STOP)
        self.action_space = spaces.Discrete(ACTION.n_actions)
        
        # Observation space
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
            'phase': spaces.Box(
                low=0, high=1,
                shape=(1,),
                dtype=np.float32
            ),
        })
        
        # Initialize state variables
        self.grid = None
        self.net_mask = None
        self.current_pos = None
        self.target_pos = None
        self.current_net = None
        self.current_path = None
        self.prev_direction = None
        self.phase = None  # 0=placement, 1=routing
        self.step_count = 0
        self.max_steps = REWARD.max_steps_per_episode if hasattr(REWARD, 'max_steps_per_episode') else 1000
        
        # Track routing info
        self.routed_nets = {}
        self.all_paths = {}
        
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """Reset the environment"""
        super().reset(seed=seed)
        
        # Initialize grid: 3 channels
        # Channel 0: Component occupied
        # Channel 1: Track occupied  
        # Channel 2: DRC forbidden
        self.grid = np.zeros((3, self.grid_height, self.grid_width), dtype=np.float32)
        
        # Initialize net mask (current network being routed)
        self.net_mask = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        
        # Place MCU (fixed position)
        self._place_mcu()
        
        # Setup board edge forbidden zone
        self._setup_board_edges()
        
        # Initialize routing state
        self.current_net = "OSC_IN"
        self.current_path = []
        self.prev_direction = (0, 0)
        self.phase = 1  # Start in routing phase
        
        # Set target to first net target (MCU Pin5 for OSC_IN)
        self.target_pos = self._get_pad_position("U1", 5)
        
        # Reset counters
        self.step_count = 0
        self.routed_nets = {}
        self.all_paths = {}
        
        return self._get_obs(), {}
    
    def step(self, action: int) -> Tuple[Dict, float, bool, bool, Dict]:
        """Execute one step"""
        self.step_count += 1
        
        reward = 0.0
        done = False
        truncated = False
        
        # Handle STOP action
        if action == 8:
            # End current net routing
            if len(self.current_path) > 0:
                # Save current path
                self._save_current_path()
                
                # Check if all nets are routed
                if self.current_net == "OSC_OUT":
                    # All nets complete
                    reward += REWARD.r_completion
                    done = True
                else:
                    # Move to next net
                    self.current_net = "OSC_OUT"
                    self.target_pos = self._get_pad_position("U1", 6)
                    self.current_path = []
                    self.prev_direction = (0, 0)
            
            obs = self._get_obs()
            info = {'step': self.step_count, 'action': 'STOP'}
            return obs, reward, done, truncated, info
        
        # Get direction (handle numpy array)
        action = int(action)
        dx, dy = ACTION_MAP[action]
        
        # Validate angle change
        if not validate_angle(self.prev_direction, (dx, dy)):
            reward += REWARD.r_angle
        
        # Calculate new position
        new_x = self.current_pos[0] + dx
        new_y = self.current_pos[1] + dy
        
        # Boundary check
        if new_x < 0 or new_x >= self.grid_width or new_y < 0 or new_y >= self.grid_height:
            reward += REWARD.r_drc_violation
            done = True
            obs = self._get_obs()
            info = {'step': self.step_count, 'action': action, 'reason': 'boundary'}
            return obs, reward, done, truncated, info
        
        # Check collision with components
        if self.grid[CH_COMPONENT, new_y, new_x] == 1:
            reward += REWARD.r_overlap
            done = True
            obs = self._get_obs()
            info = {'step': self.step_count, 'action': action, 'reason': 'component_collision'}
            return obs, reward, done, truncated, info
        
        # Check collision with other tracks (using clearance)
        clearance_grid = expand_mask(self.grid[CH_TRACK].astype(np.uint8), self.min_clearance_cells)
        if clearance_grid[new_y, new_x] == 1:
            reward += REWARD.r_overlap
            done = True
            obs = self._get_obs()
            info = {'step': self.step_count, 'action': action, 'reason': 'track_collision'}
            return obs, reward, done, truncated, info
        
        # Check DRC forbidden zones
        if self.grid[CH_DRC, new_y, new_x] == 1:
            reward += REWARD.r_drc_violation
            done = True
            obs = self._get_obs()
            info = {'step': self.step_count, 'action': action, 'reason': 'drc_violation'}
            return obs, reward, done, truncated, info
        
        # Valid move - update position
        self.current_pos = (new_x, new_y)
        self.current_path.append((new_x, new_y))
        
        # Update net mask
        self.net_mask[new_y, new_x] = 1.0
        
        # Update previous direction
        self.prev_direction = (dx, dy)
        
        # Step reward
        reward += REWARD.r_step
        
        # Distance-based reward (get closer to target)
        dist_before = abs(self.current_path[0][0] - self.target_pos[0]) + abs(self.current_path[0][1] - self.target_pos[1]) if len(self.current_path) > 1 else float('inf')
        dist_after = abs(new_x - self.target_pos[0]) + abs(new_y - self.target_pos[1])
        if dist_after < dist_before:
            reward += 1.0  # Positive reward for getting closer
        
        # Check if reached target
        if self._is_at_target():
            reward += REWARD.r_reach_target
            self._save_current_path()
            
            # Move to next net or complete
            if self.current_net == "OSC_IN":
                self.current_net = "OSC_OUT"
                self.target_pos = self._get_pad_position("U1", 6)
                self.current_path = []
                self.prev_direction = (0, 0)
            else:
                # All done
                reward += REWARD.r_completion
                done = True
        
        # Check timeout
        if self.step_count >= self.max_steps:
            truncated = True
        
        obs = self._get_obs()
        info = {
            'step': self.step_count,
            'action': action,
            'action_name': DIRECTION_NAMES[action],
            'current_pos': (grid_to_mm(self.current_pos[0]), grid_to_mm(self.current_pos[1])),
            'net': self.current_net,
        }
        
        return obs, reward, done, truncated, info
    
    def _get_obs(self) -> Dict:
        """Get observation"""
        return {
            'grid': self.grid.copy(),
            'net_mask': self.net_mask.copy(),
            'current_pos': np.array([
                self.current_pos[0] / self.grid_width,
                self.current_pos[1] / self.grid_height
            ], dtype=np.float32),
            'target_pos': np.array([
                self.target_pos[0] / self.grid_width,
                self.target_pos[1] / self.grid_height
            ], dtype=np.float32),
            'phase': np.array([self.phase], dtype=np.float32),
        }
    
    def _place_mcu(self):
        """Place MCU at fixed position"""
        mcu_mask = create_component_mask(
            (self.grid_height, self.grid_width),
            self.mcu_pos,
            self.mcu_size,
            self.resolution,
            padding=0.2  # 0.2mm clearance
        )
        self.grid[CH_COMPONENT] = mcu_mask
        
        # Create MCU forbidden zone (DRC channel)
        mcu_forbidden = create_rectangular_mask(
            (self.grid_height, self.grid_width),
            self.mcu_pos,
            self.mcu_size[0] + 2 * self.min_crystal_to_mcu,
            self.mcu_size[1] + 2 * self.min_crystal_to_mcu,
            self.resolution,
            padding=0.0
        )
        self.grid[CH_DRC] = mcu_forbidden
    
    def _setup_board_edges(self):
        """Setup board edge forbidden zones"""
        edge_mask = create_board_edge_mask(
            (self.grid_height, self.grid_width),
            BOARD.margin,
            self.resolution
        )
        self.grid[CH_DRC] = np.maximum(self.grid[CH_DRC], edge_mask)
    
    def _get_pad_position(self, ref: str, pin: int) -> Tuple[int, int]:
        """Get pad position in grid coordinates"""
        # This would normally read from component definition
        # For now, approximate positions based on typical LQFP-48 and crystal
        
        if ref == "U1":
            # Place pads outside MCU forbidden zone
            # MCU forbidden zone extends min_crystal_to_mcu beyond component edges
            mcu_left = self.mcu_pos[0] - self.mcu_size[0]/2
            forbidden_extent = DRC.min_crystal_to_mcu + 0.3  # extra margin
            
            if pin == 5:  # OSC_IN
                x = mm_to_grid(mcu_left - forbidden_extent)
                y = mm_to_grid(self.mcu_pos[1] - 1.5)
                return (x, y)
            elif pin == 6:  # OSC_OUT
                x = mm_to_grid(mcu_left - forbidden_extent)
                y = mm_to_grid(self.mcu_pos[1] + 1.5)
                return (x, y)
        
        elif ref == "Y1":
            if pin == 1:  # OSC_IN
                return (100, 200)  # Placeholder - would be set by placement
            elif pin == 3:  # OSC_OUT
                return (100, 220)  # Placeholder
        
        elif ref == "C1":
            if pin == 1:
                return (80, 200)  # Placeholder
            elif pin == 2:
                return (80, 210)  # GND
        
        elif ref == "C2":
            if pin == 1:
                return (80, 220)  # Placeholder
            elif pin == 2:
                return (80, 230)  # GND
        
        return (0, 0)
    
    def _is_at_target(self) -> bool:
        """Check if current position is at target"""
        return (self.current_pos[0] == self.target_pos[0] and 
                self.current_pos[1] == self.target_pos[1])
    
    def _save_current_path(self):
        """Save current path to routed nets"""
        if len(self.current_path) > 0:
            self.routed_nets[self.current_net] = self.current_path.copy()
            
            # Update track grid
            track_mask = create_track_mask(
                (self.grid_height, self.grid_width),
                self.current_path,
                width=1
            )
            self.grid[CH_TRACK] = np.maximum(self.grid[CH_TRACK], track_mask)
            
            # Clear net mask
            self.net_mask = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
    
    def render(self, mode: str = 'human'):
        """Render the environment"""
        if mode == 'human':
            self._render_text()
        elif mode == 'rgb_array':
            return self._render_rgb()
    
    def _render_text(self):
        """Text-based rendering"""
        print(f"\n=== Step {self.step_count} ===")
        print(f"Net: {self.current_net}")
        print(f"Position: ({grid_to_mm(self.current_pos[0]):.1f}, {grid_to_mm(self.current_pos[1]):.1f}) mm")
        print(f"Target: ({grid_to_mm(self.target_pos[0]):.1f}, {grid_to_mm(self.target_pos[1]):.1f}) mm")
        print(f"Path length: {len(self.current_path)} cells")
        
    def _render_rgb(self) -> np.ndarray:
        """RGB array rendering"""
        # Create RGB image from grid
        height, width = self.grid_height, self.grid_width
        
        # Start with dark background
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Channel 0 (components) -> Blue
        img[self.grid[CH_COMPONENT] == 1] = [0, 0, 255]
        
        # Channel 1 (tracks) -> Green
        green_mask = (self.grid[CH_TRACK] == 1) & (self.grid[CH_COMPONENT] == 0)
        img[green_mask] = [0, 255, 0]
        
        # Channel 2 (DRC forbidden) -> Red (faded)
        drc_mask = (self.grid[CH_DRC] == 1) & (self.grid[CH_TRACK] == 0) & (self.grid[CH_COMPONENT] == 0)
        img[drc_mask] = [50, 0, 0]
        
        # Current position -> Yellow
        if self.current_pos:
            y, x = self.current_pos[1], self.current_pos[0]
            if 0 <= y < height and 0 <= x < width:
                img[y, x] = [255, 255, 0]
        
        # Target position -> Magenta
        if self.target_pos:
            y, x = self.target_pos[1], self.target_pos[0]
            if 0 <= y < height and 0 <= x < width:
                img[y, x] = [255, 0, 255]
        
        # Scale up for visibility
        scale = 2
        img = np.repeat(np.repeat(img, scale, axis=0), scale, axis=1)
        
        return img
    
    def close(self):
        """Clean up"""
        pass


class SimplifiedCrystalEnv(CrystalRLEnv):
    """
    Simplified version with fixed component positions
    Focuses only on routing optimization
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        
        # Define fixed component positions - very close for easier learning
        self.crystal_pos = (28.5, 25.0)  # Y1 position (3mm from MCU)
        self.cap1_pos = (26.0, 23.5)      # C1 position
        self.cap2_pos = (26.0, 26.5)      # C2 position
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None):
        """Reset with fixed component positions"""
        # Set starting position before calling super().reset()
        self.current_pos = self._get_pad_position("U1", 5)
        
        super().reset(seed, options)
        
        # Place crystal
        crystal_mask = create_component_mask(
            (self.grid_height, self.grid_width),
            self.crystal_pos,
            self.crystal_size,
            self.resolution,
            padding=0.2
        )
        self.grid[CH_COMPONENT] = np.maximum(self.grid[CH_COMPONENT], crystal_mask)
        
        # Crystal forbidden zone (under crystal)
        crystal_forbidden = create_crystal_forbidden_zone(
            (self.grid_height, self.grid_width),
            self.crystal_pos,
            self.crystal_size,
            self.crystal_forbidden,
            self.resolution
        )
        self.grid[CH_DRC] = np.maximum(self.grid[CH_DRC], crystal_forbidden)
        
        # Place capacitors
        for cap_pos in [self.cap1_pos, self.cap2_pos]:
            cap_mask = create_component_mask(
                (self.grid_height, self.grid_width),
                cap_pos,
                self.cap_size,
                self.resolution,
                padding=0.1
            )
            self.grid[CH_COMPONENT] = np.maximum(self.grid[CH_COMPONENT], cap_mask)
        
        # Set starting position (MCU OSC_IN pin)
        self.current_pos = self._get_pad_position("U1", 5)
        
        # Set target to crystal Y1 pin 1 (for OSC_IN net)
        self.target_pos = (mm_to_grid(self.crystal_pos[0]), mm_to_grid(self.crystal_pos[1]))
        
        return self._get_obs(), {}


def make_env():
    """Create environment instance"""
    return SimplifiedCrystalEnv()


if __name__ == "__main__":
    # Test environment
    env = SimplifiedCrystalEnv()
    obs, info = env.reset()
    
    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)
    print("Grid shape:", obs['grid'].shape)
    
    # Run a few random steps
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"Step {i}: action={action}, reward={reward:.2f}, done={done}")
        
        if done or truncated:
            break
    
    env.close()
