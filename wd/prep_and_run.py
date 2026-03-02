import os
import pandas as pd
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Prepare and run CALVADOS sims sequentially on ONE GPU.")
parser.add_argument('--name', nargs='?',required=True,type=str)
parser.add_argument("--nb_rep", type=int, default=3)
#parser.add_argument("--gpu_id", type=int, default=0)
args = parser.parse_args()

N_REPLICAS = args.nb_rep
name = args.name
# gpuID = args.gpu_id

cwd = os.getcwd()

# This file will contain ALL simulation commands
master_script = os.path.join(cwd, "run_all_sims.sh")

with open(master_script, "w") as master:
    master.write("#!/bin/bash\n")
    # master.write("export CUDA_DEVICE_ORDER=PCI_BUS_ID\n")
    # master.write(f"export CUDA_VISIBLE_DEVICES={gpuID}\n\n")
    master.write("echo 'Starting sequential CALVADOS sims'\n\n")

    protein_dir = os.path.join(cwd, name)
    os.makedirs(protein_dir, exist_ok=True)

    for rep in range(1, N_REPLICAS + 1):
        print(f"  - Preparing replica {rep}")

        rep_dir = os.path.join(protein_dir, f"replica_{rep}")
        os.makedirs(rep_dir, exist_ok=True)

        input_dir = os.path.join(rep_dir, "input")
        os.makedirs(input_dir, exist_ok=True)

        # Copy residues file
        residues_src = os.path.join(cwd, "input", "residues.csv")
        residues_dst = os.path.join(input_dir, "residues.csv")
        if not os.path.exists(residues_dst):
            subprocess.run(f"cp {residues_src} {residues_dst}", shell=True)

        # Run prepare.py
        subprocess.run(
            f"python ../../prep.py --name {name} --replica_nb {rep}",
            shell=True, cwd=rep_dir
        )

        # Append simulation command to master script
        log_file = os.path.join(rep_dir, f"runtime_{rep}.log")
        master.write(
            f"echo 'Starting {name} replica {rep}'\n"
            f"python submit.py {name} {rep} >> {log_file} 2>&1\n"
            f"echo 'Finished {name} replica {rep}'\n\n"
        )               # the submit.py content is the one in the submit_all.py file

os.chmod(master_script, 0o755)

# Launch ONE tmux session
session_name = "calvados_all"
subprocess.run(["tmux", "new-session", "-d", "-s", session_name, master_script])
subprocess.run(["tmux", "set-option", "-t", session_name, "remain-on-exit", "on"])

print(f"\nLaunched ONE tmux session '{session_name}' running all simulations sequentially.")