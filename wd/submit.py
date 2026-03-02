# very minimal file since we use one tmux session for all the simulations

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description="Run a CALVADOS simulation locally with a specific GPU.")
parser.add_argument("protein1", type=str, help="Name of the first protein (e.g., asyn)")
parser.add_argument("replica", type=int, help="Replica number")
args = parser.parse_args()


cwd = os.getcwd()
# get us to /home/jtd893/Calvados2/MpipiGG_designs/ since master script runs from there
rep_nb = args.replica
system_path = os.path.join(cwd, args.protein1, f"replica_{rep_nb}", args.protein1)      
# since the run.py file is in /home/jtd893/Calvados2/MpipiGG_designs/E_Seq1/replica_1/E_Seq1


# Activate environment
# os.system("source /home/jtd893/.bashrc && conda activate calvados")         #CHANGE TO YOUR OWN USERNAME/ENVIRONMENT # Find out starting folder???

# Run sim
subprocess.run(
    f"python {system_path}/run.py --path {system_path}",
    shell=True
)