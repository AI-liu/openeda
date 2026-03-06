"""
Evaluation Script for Crystal Routing RL Agent
"""

import argparse
import os
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crystal_env import SimplifiedCrystalEnv
from ppo_agent import PPOCrystalAgent
from utils.grid_utils import compute_track_length, grid_to_mm


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Evaluate Crystal Routing RL Agent")
    
    parser.add_argument(
        '--model_path',
        type=str,
        required=True,
        help='Path to trained model'
    )
    parser.add_argument(
        '--n_episodes',
        type=int,
        default=20,
        help='Number of episodes to evaluate'
    )
    parser.add_argument(
        '--render',
        action='store_true',
        help='Render the environment'
    )
    parser.add_argument(
        '--save_results',
        type=str,
        default=None,
        help='Path to save evaluation results'
    )
    parser.add_argument(
        '--verbose',
        type=int,
        default=1,
        help='Verbosity level'
    )
    
    return parser.parse_args()


def evaluate_episode(env, agent, render=False):
    """Evaluate a single episode"""
    obs, info = env.reset()
    done = False
    truncated = False
    
    total_reward = 0
    step_count = 0
    actions = []
    
    while not (done or truncated):
        action, _ = agent.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        
        total_reward += reward
        step_count += 1
        actions.append(action)
        
        if render:
            env.render()
    
    # Get routing info
    paths = env.routed_nets
    track_lengths = {}
    
    for net_name, path in paths.items():
        length_mm = compute_track_length(path, resolution=0.1)
        track_lengths[net_name] = length_mm
    
    # Calculate symmetry
    osc_in_length = track_lengths.get("OSC_IN", 0)
    osc_out_length = track_lengths.get("OSC_OUT", 0)
    symmetry_error = abs(osc_in_length - osc_out_length)
    
    result = {
        'total_reward': total_reward,
        'step_count': step_count,
        'track_lengths': track_lengths,
        'symmetry_error': symmetry_error,
        'success': total_reward > 0,
    }
    
    return result


def main():
    """Main evaluation function"""
    args = parse_args()
    
    # Check model exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model not found at {args.model_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Crystal Routing RL Evaluation")
    print("=" * 60)
    print(f"Model: {args.model_path}")
    print(f"Episodes: {args.n_episodes}")
    print(f"Render: {args.render}")
    print("=" * 60)
    
    # Create environment
    env = SimplifiedCrystalEnv()
    
    # Create agent and load model
    agent = PPOCrystalAgent(env=env, verbose=0)
    agent.load(args.model_path)
    
    print("\nEvaluating...")
    
    results = []
    
    for episode in range(args.n_episodes):
        result = evaluate_episode(env, agent, render=args.render)
        results.append(result)
        
        if args.verbose > 0:
            status = "SUCCESS" if result['success'] else "FAILED"
            print(f"\nEpisode {episode + 1}: {status}")
            print(f"  Total Reward: {result['total_reward']:.2f}")
            print(f"  Steps: {result['step_count']}")
            print(f"  Track Lengths:")
            for net, length in result['track_lengths'].items():
                print(f"    {net}: {length:.2f}mm")
            print(f"  Symmetry Error: {result['symmetry_error']:.2f}mm")
    
    # Compute statistics
    rewards = [r['total_reward'] for r in results]
    steps = [r['step_count'] for r in results]
    symmetry_errors = [r['symmetry_error'] for r in results]
    successes = [r['success'] for r in results]
    
    all_lengths = {}
    for r in results:
        for net, length in r['track_lengths'].items():
            if net not in all_lengths:
                all_lengths[net] = []
            all_lengths[net].append(length)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Episodes: {args.n_episodes}")
    print(f"Success Rate: {np.mean(successes)*100:.1f}%")
    print(f"\nRewards:")
    print(f"  Mean: {np.mean(rewards):.2f}")
    print(f"  Std:  {np.std(rewards):.2f}")
    print(f"  Min:  {np.min(rewards):.2f}")
    print(f"  Max:  {np.max(rewards):.2f}")
    print(f"\nEpisode Lengths:")
    print(f"  Mean: {np.mean(steps):.1f}")
    print(f"  Std:  {np.std(steps):.1f}")
    print(f"\nTrack Lengths:")
    for net, lengths in all_lengths.items():
        print(f"  {net}: {np.mean(lengths):.2f} ± {np.std(lengths):.2f} mm")
    print(f"\nSymmetry Error:")
    print(f"  Mean: {np.mean(symmetry_errors):.2f} mm")
    print(f"  Std:  {np.std(symmetry_errors):.2f} mm")
    print("=" * 60)
    
    # Save results if requested
    if args.save_results:
        import json
        
        results_data = {
            'model_path': args.model_path,
            'n_episodes': args.n_episodes,
            'success_rate': float(np.mean(successes)),
            'reward_mean': float(np.mean(rewards)),
            'reward_std': float(np.std(rewards)),
            'steps_mean': float(np.mean(steps)),
            'symmetry_error_mean': float(np.mean(symmetry_errors)),
            'track_lengths': {
                net: {
                    'mean': float(np.mean(lengths)),
                    'std': float(np.std(lengths)),
                }
                for net, lengths in all_lengths.items()
            },
            'episodes': results,
        }
        
        with open(args.save_results, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to {args.save_results}")
    
    return 0 if np.mean(successes) > 0.5 else 1


if __name__ == "__main__":
    sys.exit(main())
