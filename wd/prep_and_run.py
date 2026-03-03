import argparse
import os
import shutil
import shlex
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description='Prepare and run CALVADOS sims sequentially in one tmux session.')
parser.add_argument('--name', nargs='?', required=True, type=str)
parser.add_argument('--nb_rep', type=int, default=3)
parser.add_argument('--session-name', type=str, default='calvados_all')
parser.add_argument(
    '--session-mode',
    choices=('replace', 'fail'),
    default='replace',
    help='How to handle an existing tmux session with the same name.',
)
args = parser.parse_args()

n_replicas = args.nb_rep
name = args.name
session_name = getattr(args, 'session_name', 'calvados_all')

cwd = Path.cwd()
script_dir = Path(__file__).resolve().parent
prep_script = script_dir / 'prep.py'
submit_script = script_dir / 'submit.py'

residues_src = cwd / 'input' / 'residues.csv'
if not residues_src.exists():
    raise FileNotFoundError(f'Missing residues file: {residues_src}')

master_script = cwd / 'run_all_sims.sh'

with master_script.open('w', encoding='utf-8') as master:
    master.write('#!/bin/bash\n')
    master.write('set -euo pipefail\n')
    master.write(f"cd {shlex.quote(str(cwd))}\n")
    master.write("echo 'Starting sequential CALVADOS sims'\n\n")

    protein_dir = cwd / name
    protein_dir.mkdir(parents=True, exist_ok=True)

    for rep in range(1, n_replicas + 1):
        print(f'  - Preparing replica {rep}')

        rep_dir = protein_dir / f'replica_{rep}'
        rep_dir.mkdir(parents=True, exist_ok=True)

        input_dir = rep_dir / 'input'
        input_dir.mkdir(parents=True, exist_ok=True)

        residues_dst = input_dir / 'residues.csv'
        if not residues_dst.exists():
            shutil.copy2(residues_src, residues_dst)

        subprocess.run(
            [sys.executable, str(prep_script), '--name', name, '--replica_nb', str(rep)],
            cwd=rep_dir,
            check=True,
        )

        log_file = rep_dir / f'runtime_{rep}.log'
        master.write(f"echo 'Starting {name} replica {rep}'\n")
        master.write(
            f"{sys.executable} {submit_script} {name} {rep} >> {log_file} 2>&1\n"
        )
        master.write(f"echo 'Finished {name} replica {rep}'\n\n")

os.chmod(master_script, 0o755)

session_exists = subprocess.run(
    ['tmux', 'has-session', '-t', session_name],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
).returncode == 0

if session_exists:
    if getattr(args, 'session_mode', 'replace') == 'replace':
        subprocess.run(['tmux', 'kill-session', '-t', session_name], check=True)
        print(f"Replaced existing tmux session '{session_name}'.")
    else:
        raise RuntimeError(
            f"tmux session '{session_name}' already exists. "
            "Use --session-mode replace or pass --session-name with a new name."
        )

subprocess.run(['tmux', 'new-session', '-d', '-s', session_name, str(master_script)], check=True)
subprocess.run(['tmux', 'set-option', '-t', session_name, 'remain-on-exit', 'on'], check=True)

print(f"\nLaunched tmux session '{session_name}' running all simulations sequentially.")
print(f"Attach with: tmux attach -t {session_name}")
