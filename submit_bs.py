#!/bin/env python
from optparse import OptionParser
import os, sys, re
import time
import glob
parser = OptionParser()

parser.add_option("-q", "--queue", action="store", help="queue", default='1')
parser.add_option("-s", "--seed", action="store", help="random seed", default='1')
parser.add_option("-M","--dataset-mc",action="store", help="name of MC",default = "Pythia8EPOS")
parser.add_option("-D","--dataset-data",action="store", help="name of MC",default = "Zerobias")
parser.add_option("-m","--machine",action="store",help="unfolding method",default="multifold")
parser.add_option("-a","--arguments-train",action="store", help="other arguments for training",default = "-e 50 -ui 4 --weight-clip-max 10.0 --save-best-only --ensemble 4 --eff-acc")

(opts, args) = parser.parse_args()

if opts.machine=="multifold":
  unfold = "manyfold"
else:
  unfold = opts.machine

template = """#!/bin/bash
#
#SBATCH --job-name=test_job 
#SBATCH --account=gpu_gres               # to access gpu resources
#SBATCH --partition=gpu                                           
#SBATCH --nodes=1                       # request to run job on single node                                       
#SBATCH --ntasks=10                    # request 10 CPU's (t3gpu01/02: balance between CPU and GPU : 5CPU/1GPU)      
##SBATCH --mem-per-cpu=10G
#SBATCH --gres=gpu:1                     # request  for two GPU's on machine, this is total  amount of GPUs for job        
#SBATCH --mem=40G                     # memory (per job)
#SBATCH --time=10:00:00                   # time  in format DD-HH:MM


# each node has local /scratch space to be used during job run
mkdir -p /scratch/$USER/${{SLURM_JOB_ID}}
export TMPDIR=/scratch/$USER/${{SLURM_JOB_ID}}


# Slurm reserves two GPU's (according to requirement above), those ones that are recorded in shell variable CUDA_VISIBLE_DEVICES
echo CUDA_VISIBLE_DEVICES : $CUDA_VISIBLE_DEVICES
cp mytrain.py ${{TMPDIR}}/.
cp omnifold.py ${{TMPDIR}}/.
cd ${{TMPDIR}}
python mytrain.py -m {method} -u {unfold} -mc {MC} -data {data} {arguments_train} --MCbootstrap --MCbsseed {seed} 
rm -rf /scratch/$USER/${{SLURM_JOB_ID}}
"""

for seed in range(int(opts.seed),int(opts.seed)+int(opts.queue)):
  script_name = "train_MCbs_"+str(seed)+".sh"
  infile = template.format(method = opts.machine,unfold = unfold, MC = opts.dataset_mc, data = opts.dataset_data, arguments_train = opts.arguments_train, seed=seed)
  script=open(script_name,'w')
  script.write(infile)
  script.close()
  os.system("sbatch "+script_name)


