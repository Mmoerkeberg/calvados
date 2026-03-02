# very minimal file since we use one tmux session for all the simulations

import argparse
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description='Run a CALVADOS simulation for one replica.')
parser.add_argument('protein1', type=str, help='Simulation name (system folder name)')
parser.add_argument('replica', type=int, help='Replica number')
args = parser.parse_args()

cwd = Path.cwd()
rep_nb = args.replica
system_path = cwd / args.protein1 / f'replica_{rep_nb}' / args.protein1
run_py = system_path / 'run.py'

if not run_py.exists():
    raise FileNotFoundError(
        f'Missing {run_py}. Preparation step failed or was executed from the wrong directory.'
    )

subprocess.run(
    [sys.executable, str(run_py), '--path', str(system_path)],
    check=True,
)
