#!/bin/env python
from optparse import OptionParser
import os, sys, re
import time
import glob
parser = OptionParser()

parser.add_option("-M","--dataset-mc",action="store", help="name of MC",default = "Pythia8EPOS")
parser.add_option("-D","--dataset-data",action="store", help="name of MC",default = "Pythia8CP1")
parser.add_option("-m","--machine",action="store",help="unfolding method",default="multifold")
parser.add_option("-d","--dir",action="store",help="the directory for data weights",default = "/work/jinw/omnifold/OmniFold/results_multifold_maxweight10_MCEPOS_unfoldCP1_1p3M_ensemble4_normXS/weights")
parser.add_option("-w","--preweight-choice",action="store",help="the MC weights from the systematic template",default="default")
parser.add_option("-a","--arguments-train",action="store", help="other arguments for training",default = "-e 50 -ui 4 --weight-clip-max 10.0 --save-best-only --ensemble 4 --eff-acc")

(opts, args) = parser.parse_args()

if opts.machine=="multifold":
  unfold = "manyfold"
else:
  unfold = opts.machine

weight_list = os.listdir(opts.dir)
bs_list = [re.search(r'\d+',re.search(r'bs_\d+_dataweight',string).group()).group() for string in weight_list if re.search(r'bs_\d+_dataweight',string)]

template = """#!/bin/bash
#SBATCH -p long
#SBATCH --job-name=test_job 
#SBATCH --account=t3               # to access gpu resources
#SBATCH --mem=10G                     # memory (per job)
#SBATCH --time=1-12:00:00                   # time  in format DD-HH:MM


# each node has local /scratch space to be used during job run
mkdir -p /scratch/$USER/${{SLURM_JOB_ID}}
export TMPDIR=/scratch/$USER/${{SLURM_JOB_ID}}


# Slurm reserves two GPU's (according to requirement above), those ones that are recorded in shell variable CUDA_VISIBLE_DEVICES
echo CUDA_VISIBLE_DEVICES : $CUDA_VISIBLE_DEVICES
cp mytrain.py ${{TMPDIR}}/.
cp omnifold.py ${{TMPDIR}}/.
cd ${{TMPDIR}}
python mytrain.py -m {method} -u {unfold} -mc {MC} -data {data} {arguments_train} -n _bs_{seed}_{MCweight} --preweight --preweight-choice {MCweight} --dataweight {dataweight} --results-path {outdir}
rm -rf /scratch/$USER/${{SLURM_JOB_ID}}
"""

for seed in bs_list:
  if seed == "1": continue 
  script_name = "train_bs_"+str(seed)+"_"+opts.preweight_choice+".sh"
  dataweight = os.path.join(opts.dir,"ManyFold_DNN_Rep-0_bs_"+seed+"_dataweight.npy")
  infile = template.format(method = opts.machine,unfold = unfold, MC = opts.dataset_mc, data = opts.dataset_data, arguments_train = opts.arguments_train, seed=seed, MCweight = opts.preweight_choice,dataweight=dataweight,outdir = opts.dir)
  script=open(script_name,'w')
  script.write(infile)
  script.close()
  os.system("sbatch "+script_name)


