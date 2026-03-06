#!/usr/bin/env python3
"""
Fix Python path and run scripts in pcb_rl environment
"""
import sys
import os

# Add conda env paths to front
env_paths = [p for p in sys.path if 'miniconda3' in p]
other_paths = [p for p in sys.path if 'miniconda3' not in p]
sys.path = env_paths + other_paths

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('script', help='Script to run (train.py, evaluate.py, etc.)')
    parser.add_argument('args', nargs='*', help='Arguments to pass to script')
    args = parser.parse_args()
    
    # Execute the script
    with open(args.script) as f:
        code = compile(f.read(), args.script, 'exec')
        exec(code, {'__name__': '__main__', '__file__': args.script})
