"""
Training Script for Crystal Routing RL Agent
"""

import argparse
import os
import sys
import torch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TRAINING
from crystal_env import SimplifiedCrystalEnv
from ppo_agent import PPOCrystalAgent, create_agent


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Train Crystal Routing RL Agent")
    
    parser.add_argument(
        '--timesteps', 
        type=int, 
        default=TRAINING.total_timesteps,
        help='Total training timesteps'
    )
    parser.add_argument(
        '--n_envs', 
        type=int, 
        default=1,
        help='Number of parallel environments'
    )
    parser.add_argument(
        '--model_dir',
        type=str,
        default='./models',
        help='Directory to save models'
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='./logs',
        help='Directory for tensorboard logs'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help='Device to use for training'
    )
    parser.add_argument(
        '--load_model',
        type=str,
        default=None,
        help='Path to load existing model'
    )
    parser.add_argument(
        '--save_freq',
        type=int,
        default=TRAINING.save_freq,
        help='Frequency to save model'
    )
    parser.add_argument(
        '--verbose',
        type=int,
        default=1,
        help='Verbosity level'
    )
    
    return parser.parse_args()


def main():
    """Main training function"""
    args = parse_args()
    
    # Print configuration
    print("=" * 60)
    print("Crystal Routing RL Training")
    print("=" * 60)
    print(f"Total timesteps: {args.timesteps}")
    print(f"Parallel environments: {args.n_envs}")
    print(f"Model directory: {args.model_dir}")
    print(f"Log directory: {args.log_dir}")
    print(f"Device: {args.device}")
    print(f"Save frequency: {args.save_freq}")
    print("=" * 60)
    
    # Check GPU availability
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        if device == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Create directories
    os.makedirs(args.model_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)
    
    # Create environment
    print("\nCreating environment...")
    env = SimplifiedCrystalEnv()
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    
    # Create agent
    print("\nCreating PPO agent...")
    agent = PPOCrystalAgent(
        env=env,
        model_dir=args.model_dir,
        log_dir=args.log_dir,
        device=args.device,
        verbose=args.verbose,
    )
    
    # Load existing model if specified
    if args.load_model:
        print(f"\nLoading model from {args.load_model}...")
        agent.load(args.load_model)
    
    # Train
    print("\nStarting training...")
    agent.train(
        total_timesteps=args.timesteps,
        save_freq=args.save_freq,
    )
    
    # Save final model
    final_model_path = os.path.join(args.model_dir, "crystal_ppo_final")
    agent.save(final_model_path)
    print(f"\nFinal model saved to {final_model_path}")
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluating trained agent...")
    print("=" * 60)
    
    results = agent.evaluate(env=env, n_episodes=10, render=False)
    
    print(f"\nEvaluation Results:")
    print(f"  Mean Reward: {results['mean_reward']:.2f} ± {results['std_reward']:.2f}")
    print(f"  Mean Episode Length: {results['mean_length']:.1f}")
    print(f"  Success Rate: {results['success_rate']*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
