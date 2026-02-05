###############################
# Slurm Workload Manager
# Python Wrapper
#
# Guriang-HPC
#
# 2021, rosandi
#

import os
from subprocess import check_output as runshell
from time import sleep

current_jobid=0
batch_running=False

batch_format_info='''
batch_default= {
  'name'='NONAME',          # name of the job
  'partition'='whale',      # partition to use to run the job
  'nodes'=1,                # number of nodes required
  'cores'=1,                # number of cores
  'threads'=1,              # number of threads per-core
  'param'=[par,...]         # anythings executed before running the script
  'script'='',              # the script to be executed
  'source'=(fname,content), # put content in fname as source
  'env'=['ENAME=VALUE',...] # special environment settings
}
'''

# The defaults can be overriden using env field

default_parti='whale'
default_env = {
  'all':['OMP_PROC_BIND=true', 
         'NUMBA_NUM_THREADS=$SLURM_NPROCS' 
         ],
  'whale':['OMPI_MCA_btl_vader_single_copy_mechanism=none']
}

def squeue(par=""):
    par=par.split()
    cmd=['squeue']+par
    print(runshell(cmd).decode('ascii'))

def sinfo(par=""):
    par=par.split()
    cmd=['sinfo']+par
    print(runshell(cmd).decode('ascii'))

def exists(jobid):
    ex=False
    ss=runshell('squeue').decode('ascii')
    ss=ss.split("\n")
    for s in ss:
        s=s.strip()
        if s.find("%d "%jobid) == 0:
            ex=True
            break
    return ex

def salloc(prg,par=""):
    prg=prg.split()
    par=par.split()
    cmd=['salloc']+par+prg
    print(runshell(cmd).decode('ascii'))

def srun(prg,par=""):
    prg=prg.split()
    par=par.split()
    cmd=['srun']+par+prg
    print(runshell(cmd).decode('ascii'))

def mpirun(prg,par='',python=True):
    if python:
        prg='mpirun python3 '+prg
    else:
        prg='mpirun '+prg

    salloc(prg,par)
    
def scontrol(par):
    par=par.split()
    cmd=['scontrol']+par
    print(runshell(cmd).decode('ascii'))

def sinfo(par=''):
    par=par.split()
    cmd=['sinfo']+par
    print(runshell(cmd).decode('ascii'))
    
def scancel(jobid,par=""):
    par=par.split()
    cmd=['scancel','{}'.format(jobid)]+par
    print(runshell(cmd).decode('ascii'))
    print("\n")
    sleep(2)
    squeue()

def sbatch(b,par="",submit=True):
    global current_jobid,batch_running
    
    if type(b) is str:
        # assume only a script is submitted
        b={'script':b}

    if exists(current_jobid):
        print("job %d is still running. Cancel first to submit job from this notebook"%current_jobid)
        return current_jobid
      
    if not 'script' in b:
        print("at least a 'script' should be defined in a dictionary")
        return 0

    rets=''
    retv=0
    par=par.split()
    cmd=['sbatch']+par # additional command-line parameters
    scr ='#!/bin/bash\n'

    if 'partition' in b:
        partition=b['partition']
    else:
        partition=default_parti

    if 'name' in b:
        scr+='#SBATCH --job-name='+b['name']+'\n'

    scr+='#SBATCH -p {}\n'.format(partition)
    
    if 'nodes' in b:
        scr+="#SBATCH -N {}\n".format(b['nodes'])

    if 'cores' in b:
        scr+="#SBATCH -n {}\n".format(b['cores'])

    if 'threads' in b:
        scr+='#SBATCH --ntasks-per-core={}\n'.format(b['threads'])
    
    if 'mail' in b:
        scr+='#SBATCH --mail-type={}\n'.format(b['mail'][0])
        scr+='#SBATCH --mail-user={}\n\n'.format(b['mail'][1])
    
    # default environment
    if 'all' in default_env:
        for env in default_env['all']:
            scr+="export "+env+"\n"
    
    # set default envs if partition is allocated
    if partition in default_env:
        for env in default_env[partition]:
            scr+="export "+env+"\n"

    if 'param' in b:
        for xpar in b['param']:
            scr+=xpar+"\n"
            
    if 'env' in b:
        for xenv in b['env']:
            scr+="export "+xenv+"\n"
    
    if 'source' in b:
        # This is to create a source into file defined in the second element.
        # The created file can be used in the script
        # first element: file name
        # second: source string
        with open(b['source'][0],'w') as tf:
            tf.write(b['source'][1])
            tf.write("\n")

    # THE SCRIPT to be executed
    scr+=b['script']+"\n"

    with open('submit.bash','w') as sf:
        sf.write(scr)
    
    if submit:
        cmd.append('submit.bash')
        rets=runshell(cmd).decode('ascii')
        print(rets,"\n")
    else:
        print("submit script created")
    
    if rets.find("Submitted batch job ")==0:
        retv=eval(rets.replace("Submitted batch job ",""))
    
    current_jobid=retv

    return retv

def out(jobid, tail=10):
    
    if not exists(jobid):
        print('job %d does not exist'%jobid)
        return
    
    cc='scontrol show job %d'%jobid
    ss=runshell(cc.split()).decode('ascii')
    ss=ss.split("\n")
    outf=None

    for s in ss:
        s=s.strip()
        if s.find('StdOut=')==0:
            outf=s.replace('StdOut=','')
            break
            
    if outf:
        with open(outf) as oo:
            lines=oo.read().split("\n")
        
        if tail:
            n=len(lines)-tail
            for s in lines[n:]:
                print(s)
        else:
            for s in lines:
                print(s)

### These to make life easier... MACROS ###

def nodes(nn=''):
    scontrol('show nodes '+nn)

def part(pp=''):
    scontrol('show part '+pp)

def job(jj=''):
    scontrol('show job '+jj)
