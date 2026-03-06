#!/bin/bash
# Run pcb_rl scripts in conda environment

# Source conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate pcb_rl

# Fix Python path by reordering
cd "$(dirname "$0")"

python -c "
import sys

# Move conda env path to front
env_paths = [p for p in sys.path if 'miniconda3' in p]
other_paths = [p for p in sys.path if 'miniconda3' not in p]
sys.path = env_paths + other_paths

# Import and run the main module
import train
train.main()
" "$@"
