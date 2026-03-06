"""
PPO Agent for Crystal Routing Optimization
Uses Stable-Baselines3 with custom policy network
"""

import os
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from typing import Dict, Tuple, Optional, Any
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.callbacks import BaseCallback

from config import TRAINING
from crystal_env import CrystalRLEnv, SimplifiedCrystalEnv


class GridFeatureExtractor(BaseFeaturesExtractor):
    """
    Custom feature extractor for grid-based observations
    Uses CNN for grid and MLP for position features
    """
    
    def __init__(self, observation_space, features_dim: int = 256):
        super().__init__(observation_space, features_dim)
        
        # Grid CNN encoder (for 3-channel grid)
        # Input: (3, 500, 600) - height, width
        n_input_channels = observation_space['grid'].shape[0]
        
        self.grid_cnn = nn.Sequential(
            # Conv block 1
            nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.ReLU(),
            # Conv block 2
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.ReLU(),
            # Conv block 3
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten(),
        )
        
        # Calculate CNN output size
        with torch.no_grad():
            dummy_input = torch.zeros(1, n_input_channels, 500, 600)
            cnn_output_size = self.grid_cnn(dummy_input).shape[1]
        
        # Position features MLP
        # Inputs: net_mask (500*600), current_pos (2), target_pos (2), phase (1)
        net_mask_size = observation_space['net_mask'].shape[0] * observation_space['net_mask'].shape[1]
        pos_size = observation_space['current_pos'].shape[0]
        target_size = observation_space['target_pos'].shape[0]
        phase_size = observation_space['phase'].shape[0]
        
        total_pos_features = net_mask_size + pos_size + target_size + phase_size
        
        self.pos_mlp = nn.Sequential(
            nn.Linear(total_pos_features, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        
        # Combine CNN and MLP outputs
        self.fusion = nn.Sequential(
            nn.Linear(cnn_output_size + 64, features_dim),
            nn.ReLU(),
        )
        
    def forward(self, observations: Dict[str, torch.Tensor]) -> torch.Tensor:
        # Process grid
        grid = observations['grid']
        grid_features = self.grid_cnn(grid)
        
        # Process position features
        net_mask = observations['net_mask'].flatten(1)
        current_pos = observations['current_pos']
        target_pos = observations['target_pos']
        phase = observations['phase']
        
        pos_features = torch.cat([net_mask, current_pos, target_pos, phase], dim=1)
        pos_features = self.pos_mlp(pos_features)
        
        # Combine
        combined = torch.cat([grid_features, pos_features], dim=1)
        output = self.fusion(combined)
        
        return output


class TensorBoardCallback(BaseCallback):
    """Custom callback for logging training metrics"""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        
    def _on_step(self) -> bool:
        # Log rewards periodically
        if len(self.model.ep_info_buffer) > 0:
            for info in self.model.ep_info_buffer:
                if 'r' in info:
                    self.episode_rewards.append(info['r'])
                if 'l' in info:
                    self.episode_lengths.append(info['l'])
        
        # Log every 1000 steps
        if self.n_calls % 1000 == 0:
            if len(self.episode_rewards) > 0:
                mean_reward = np.mean(self.episode_rewards[-100:])
                mean_length = np.mean(self.episode_lengths[-100:]) if self.episode_lengths else 0
                
                self.logger.record('train/mean_reward', mean_reward)
                self.logger.record('train/mean_episode_length', mean_length)
                
                if self.verbose > 0:
                    print(f"Step {self.n_calls}: mean_reward={mean_reward:.2f}, mean_length={mean_length:.0f}")
        
        return True


class PPOCrystalAgent:
    """
    PPO Agent for Crystal Routing
    
    Wraps Stable-Baselines3 PPO with custom configuration
    """
    
    def __init__(
        self,
        env,
        model_dir: str = "./models",
        log_dir: str = "./logs",
        device: str = "auto",
        verbose: int = 1
    ):
        self.env = env
        self.model_dir = model_dir
        self.log_dir = log_dir
        
        # Create directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # Policy kwargs for custom feature extractor
        policy_kwargs = {
            'features_extractor_class': GridFeatureExtractor,
            'features_extractor_kwargs': {'features_dim': 256},
            'net_arch': [dict(pi=[256, 128], vf=[256, 128])],
        }
        
        # Create PPO model
        self.model = PPO(
            "MultiInputPolicy",
            env,
            learning_rate=TRAINING.learning_rate,
            n_steps=TRAINING.n_steps,
            batch_size=TRAINING.batch_size,
            n_epochs=TRAINING.n_epochs,
            gamma=TRAINING.gamma,
            gae_lambda=TRAINING.gae_lambda,
            clip_range=TRAINING.clip_range,
            ent_coef=TRAINING.ent_coef,
            vf_coef=TRAINING.vf_coef,
            max_grad_norm=TRAINING.max_grad_norm,
            policy_kwargs=policy_kwargs,
            verbose=verbose,
            tensorboard_log=log_dir,
            device=device,
        )
        
        self.callback = TensorBoardCallback(verbose=verbose)
        
    def train(
        self,
        total_timesteps: int = None,
        eval_env=None,
        eval_freq: int = None,
        save_freq: int = None,
    ) -> None:
        """Train the agent"""
        
        if total_timesteps is None:
            total_timesteps = TRAINING.total_timesteps
        
        if eval_freq is None:
            eval_freq = TRAINING.eval_freq
            
        if save_freq is None:
            save_freq = TRAINING.save_freq
        
        print(f"Starting training for {total_timesteps} timesteps...")
        
        # Create eval callback if eval_env provided
        callbacks = [self.callback]
        
        # Train
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks,
            progress_bar=True,
        )
        
        print("Training complete!")
        
    def predict(self, observation, deterministic: bool = True) -> Tuple[int, np.ndarray]:
        """Predict action"""
        return self.model.predict(observation, deterministic=deterministic)
    
    def save(self, path: str = None) -> None:
        """Save model"""
        if path is None:
            path = os.path.join(self.model_dir, "crystal_ppo")
        
        self.model.save(path)
        print(f"Model saved to {path}")
        
    def load(self, path: str) -> None:
        """Load model"""
        self.model = PPO.load(path, env=self.env)
        print(f"Model loaded from {path}")
        
    def evaluate(self, env=None, n_episodes: int = 10, render: bool = False) -> Dict[str, float]:
        """Evaluate the agent"""
        
        if env is None:
            env = self.env
            
        episode_rewards = []
        episode_lengths = []
        success_count = 0
        
        for episode in range(n_episodes):
            obs, info = env.reset()
            done = False
            truncated = False
            episode_reward = 0
            episode_length = 0
            
            while not (done or truncated):
                action, _ = self.predict(obs, deterministic=True)
                obs, reward, done, truncated, info = env.step(action)
                episode_reward += reward
                episode_length += 1
                
                if render:
                    env.render()
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            # Consider success if positive reward
            if episode_reward > 0:
                success_count += 1
            
            print(f"Episode {episode + 1}: reward={episode_reward:.2f}, length={episode_length}")
        
        results = {
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'mean_length': np.mean(episode_lengths),
            'success_rate': success_count / n_episodes,
        }
        
        return results


def create_agent(
    n_envs: int = 1,
    model_dir: str = "./models",
    log_dir: str = "./logs",
    device: str = "auto",
    verbose: int = 1,
) -> PPOCrystalAgent:
    """Create PPO agent with environment"""
    
    # Create environment
    if n_envs > 1:
        from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
        
        def make_env():
            return SimplifiedCrystalEnv()
        
        if n_envs > 1:
            env = SubprocVecEnv([make_env for _ in range(n_envs)])
        else:
            env = DummyVecEnv([make_env])
    else:
        env = SimplifiedCrystalEnv()
    
    # Create agent
    agent = PPOCrystalAgent(
        env=env,
        model_dir=model_dir,
        log_dir=log_dir,
        device=device,
        verbose=verbose,
    )
    
    return agent


if __name__ == "__main__":
    # Test agent creation
    print("Creating agent...")
    agent = create_agent(n_envs=1, verbose=1)
    print("Agent created successfully!")
    print(f"Policy: {agent.model.policy}")
