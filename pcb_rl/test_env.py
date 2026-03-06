#!/usr/bin/env python3
"""
Quick test script for PCB RL Crystal environment
"""
import sys

# Fix Python path
env_paths = [p for p in sys.path if 'miniconda3' in p]
other_paths = [p for p in sys.path if 'miniconda3' not in p]
sys.path = env_paths + other_paths

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from crystal_env import SimplifiedCrystalEnv
from ppo_agent import PPOCrystalAgent
from config import TRAINING

def test_environment():
    """Test the environment"""
    print("=" * 60)
    print("Testing Crystal RL Environment")
    print("=" * 60)
    
    env = SimplifiedCrystalEnv()
    obs, info = env.reset()
    
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    print(f"Grid shape: {obs['grid'].shape}")
    print(f"Net mask shape: {obs['net_mask'].shape}")
    
    # Test random actions
    print("\nTesting random actions...")
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"  Step {i}: action={action}, reward={reward:.2f}, done={done}")
        if done or truncated:
            break
    
    print("\n✓ Environment test passed!")
    return True


def test_agent():
    """Test the PPO agent"""
    print("\n" + "=" * 60)
    print("Testing PPO Agent")
    print("=" * 60)
    
    env = SimplifiedCrystalEnv()
    
    agent = PPOCrystalAgent(
        env=env,
        model_dir="./models",
        log_dir="./logs",
        device="cpu",
        verbose=0
    )
    
    print("Agent created successfully!")
    print(f"Policy: {agent.model.policy}")
    
    # Quick test with few training steps
    print("\nQuick training test (100 steps)...")
    agent.train(total_timesteps=100)
    
    print("\n✓ Agent test passed!")
    return True


def main():
    print("PCB RL Crystal Environment - Quick Test")
    print()
    
    # Test environment
    if not test_environment():
        print("✗ Environment test failed!")
        return 1
    
    # Test agent (optional - comment out for quick test)
    # if not test_agent():
    #     print("✗ Agent test failed!")
    #     return 1
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    print("\nTo train the model, run:")
    print("  cd pcb_rl")
    print("  source ~/miniconda3/etc/profile.d/conda.sh")
    print("  conda activate pcb_rl")
    print("  python -c \";")
    print('    import sys')
    print('    env_paths = [p for p in sys.path if miniconda3 in p]')
    print('    other_paths = [p for p in sys.path if miniconda3 not in p]')
    print('    sys.path = env_paths + other_paths')
    print('    exec(open(train.py).read())')
    print('  ;"')
    
    return 0


if __name__ == "__main__":
    exit(main())
