import os
from argparse import ArgumentParser

from calvados.cfg import Components, Config

parser = ArgumentParser()
parser.add_argument('--name', nargs='?', required=True, type=str)
parser.add_argument('--replica_nb', type=int, required=True, help='Replica number (integer)')
args = parser.parse_args()

cwd = os.getcwd()  # should be the replica folder (e.g., RG/replica_1)
sysname = args.name
replica = args.replica_nb

# create system folder (where configs will go)
path = os.path.join(cwd, sysname)
os.makedirs(path, exist_ok=True)

# output folder for data
output_dir = os.path.join(cwd, f'data_{replica}')
os.makedirs(output_dir, exist_ok=True)

residues_file = os.path.join(cwd, 'input', 'residues.csv')

L = 50              # set the side length of the cubic box
N_save = 7000       # set the saving interval (number of integration steps)
N_frames = 1010     # set final number of frames to save

config = Config(
  # GENERAL
  sysname=sysname,  # name of simulation system
  box=[L, L, L],  # nm
  temp=300,  # K
  ionic=0.19,  # M
  pH=7.5,
  topol='center',

  # RUNTIME SETTINGS
  wfreq=N_save,  # dcd writing interval, 1 = 10 fs
  steps=N_frames * N_save,  # number of simulation steps
  runtime=0,  # overwrites 'steps' keyword if > 0
  platform='CPU',  # CPU or CUDA
  restart='checkpoint',
  frestart='restart.chk',
  verbose=True,
)

analyses = f"""

from calvados.analysis import save_conf_prop

save_conf_prop(path=\"{path:s}\",name=\"{sysname:s}\",residues_file=\"{residues_file:s}\",output_path=\"{output_dir}\",start=10,is_idr=False,select='all')
"""

config.write(path, name='config.yaml', analyses=analyses)

components = Components(
  # Defaults
  molecule_type='protein',
  nmol=1,  # number of molecules
  restraint=True,  # apply restraints
  charge_termini='both',  # charge N or C or both

  # INPUT
  fresidues=f'{cwd}/input/residues.csv',  # residue definitions
  pdb_folder=f'{cwd}/input',  # directory for pdb and PAE files

  # RESTRAINTS
  restraint_type='go',  # harmonic or go
  use_com=True,  # apply on centers of mass instead of CA
  colabfold=0,  # PAE format (EBI AF=0, Colabfold=1&2)
  k_go=15.,  # Restraint force constant
)

components.add(name=args.name)
components.write(path, name='components.yaml')
