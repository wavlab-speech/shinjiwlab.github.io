---
layout: post
title: Delta Usage
date: 2023-04-01 09:00:00-0800
description: Delta cluster usage.
comments: false
---

# Account creation
- Create an account for NCSA on [ACCESS](https://allocations.access-ci.org/)
- Send the username to allocation managers (e.g. William, wc4@andrew.cmu.edu) to add the user in our group.

## login
* Delta: check https://wiki.ncsa.illinois.edu/display/DSC/Delta+User+Guide#DeltaUserGuide-DirectAccesslogin_nodes

# Important
1. `Home` directory is of limited space. Please do most of your work in storage directories (`$ cd /work/hdd` or `$ cd /work/nvme`).
2. When you publish a paper, please **acknowledge the Delta and ACCESS**. We will get benefit when we apply for Delta credits next time.
   * [Acknowledgement webpage](https://access-ci.org/about/acknowledging-access/)
      * Example: Experiments of this work used the Bridges2 system at PSC and Delta system at NCSA through allocations CIS210014 and IRI120008P from the Advanced Cyberinfrastructure Coordination Ecosystem: Services \& Support (ACCESS) program, supported by National Science Foundation grants \#2138259,\#tel:2138286, \#tel:2138307, \#tel:2137603, and \#tel:2138296.

# Summary of NCSA usage and the partitions
* NCSA has limited service units (SUs) for resource availability.
* [General user guide for Delta](https://wiki.ncsa.illinois.edu/display/DSC/Delta+User+Guide)
* `sinfo` lists all the available partitions in NCSA and their status.
<table class="table">
    <thead>
        <tr>
            <th> </th>
            <th> NCSA (Delta) </th>
        </tr>
     </thead>
     <tbody>
        <tr>
            <td>Partitions</td>
            <td>cpu, gpuA100x4, gpuA100x8, gpuA40x4, gpuMI100x8 </td>
        </tr>
        <tr>
            <td>  GPU resources</td>
            <td>gpuA100x4, gpuA100x8, gpuA40x4, gpuMI100x8 </td>
        </tr>
        <tr>
            <td>  CPU resources</td>
            <td>cpu</td>
        </tr>
        <tr>
            <td>Default</td>
            <td>cpu</td>
        </tr>
     </tbody>
</table>

## Other usage
* Submitting jobs with dependency
  * This can be used to submit a job which is expected to start run after some specific jobs finish. In many cases, training a model can take a few days. However, Delta has the restriction that each job can run for 2 days at most. In this case, we can start a job with dependency for long jobs. For example, you already start a job ID is 000001 and you want a following job right after it. You can submit jobs like:
    ```
      sbatch --time 2-0:00:00 --dependency=afterany:000001 run.sh
    ```
 
* Common arguments in sbatch / srun
  ```
  -p, --partition=partition               partition requested
  -J, --job-name=jobname                  name of job
  -t, --time=time                         time limit
  --gres=rsrc_name[:rsrc_type]:rsrc_num   required generic resources
  -c, --cpus-per-task=ncpus               number of cpus required per task
  -d, --dependency=type:jobid[:time]      defer job until condition on jobid is satisfied
  -e, --error=err                         file for batch script's standard error
  -o, --output=out                        file for batch script's standard output
  --mem-per-cpu=MB                        maximum amount of real memory per allocated
  --ntasks-per-node=n                     number of tasks to invoke on each node
  --reservation=name                      allocate resources from named reservation, e.g. `GPUcis210027`
  ```

* View tools
  * slurm commands
    ```
    # view jobs in the queue
    squeue -u ${username}
     
    # view detailed job info
    scontrol show jobid -d ${jobid}
     
    # view job history and billing info, e.g. since time 04/22/2022 12am.
    sacct -u ${username} -S 2022-04-22T00:00:00 --format=JobID,jobname,user,elapsed,nnodes,alloccpus,state,partition,nodelist,AllocTRES%50,CPUTime 
    ```
  * Delta provides `slurm-tool`
    ```
    # Show or watch job queue:
    slurm-tool [watch] queue     show own jobs
    slurm-tool [watch] q <user>  show user's jobs
    slurm-tool [watch] quick     show quick overview of own jobs
    slurm-tool [watch] shorter   sort and compact entire queue by job size
    slurm-tool [watch] short     sort and compact entire queue by priority
    slurm-tool [watch] full      show everything
    slurm-tool [w] [q|qq|ss|s|f] shorthands for above!

    slurm-tool qos               show job service classes
    slurm-tool top [queue|all]   show summary of active users

    # Show detailed information about jobs:
    slurm-tool prio [all|short]  show priority components
    slurm-tool j|job <jobid>     show everything else
    slurm-tool steps <jobid>     show memory usage of running srun job steps

    # Show usage and fair-share values from accounting database:
    slurm-tool h|history <time>  show jobs finished since, e.g. "1day" (default)
    slurm-tool shares

    # Show nodes and resources in the cluster:
    slurm-tool p|partitions      all partitions
    slurm-tool n|nodes           all cluster nodes
    slurm-tool c|cpus            total cpu cores in use
    slurm-tool cpus <partition>  cores available to partition, allocated and free
    slurm-tool cpus jobs         cores/memory reserved by running jobs
    slurm-tool cpus queue        cores/memory required by pending jobs
    slurm-tool features          List features and GRES

    # Other:
    slurm-tool v|version         Print versions of slurm-tool tool and slurm itself
    ```

# ESPnet installation steps

## ESPnet installation

You can generally follow the [ESPnet installation guide](https://espnet.github.io/espnet/installation.html).

## Kaldi installation steps (Delta)
   ```bash
   git clone https://github.com/kaldi-asr/kaldi
   cd kaldi/tools
   conda create --name py2 python=2.7 # assume you already have conda environment
   conda activate py2
   conda install -c anaconda mkl mkl-include
   conda install -c conda-forge subversion sox
   make -j 8
   ./extras/install_irstlm.sh # Optional
   cd ../src/
   ./configure --use-cuda=no --mkl-root=<conda_root>/envs/py2
   make -j clean depend; make -j 8
   ```

## Running ESPnet using slurm backend
Modify `cmd.sh` and `conf/slurm.conf` to be ready for slurm management
   ```bash
   # cmd.sh

   # line 31
   cmd_backend='slurm'  # cmd_backend='local'
   ```
```yaml
# conf/slurm.conf

# Default configuration
command sbatch --export=PATH
option name=* --job-name $0
default time=2-00:00:00
option time=* --time $0
option mem=* --mem-per-cpu $0
option mem=0
option num_threads=* --cpus-per-task $0
option num_threads=1 --cpus-per-task 1
option num_nodes=* --nodes $0
default gpu=0
option gpu=0 -p cpu --mem-per-cpu 2000M --account=bbjs-delta-cpu
option gpu=1 -p gpuA40x4 --gres=gpu:1 -c 16 --mem 60000M --account=bbjs-delta-gpu
option gpu=4 -p gpuA40x4 --gres=gpu:4 -c 64 --mem 240000M --account=bbjs-delta-gpu
option gpu=* -p gpuA40x4 --gres=gpu:$0 -c 32 --mem 120000M --account=bbjs-delta-gpu
# Recommend allocating more CPU than, or equal to the number of GPU
# note: the --max-jobs-run option is supported as a special case
# by slurm.pl and you don't have to handle it in the config file.
```

## Running other jobs using slurm backend
1. Initiate a bash scripts `run.sh` as

```bash
#!/bin/bash

python run.py
```

2. Submit the bash script using `sbatch`

```bash
sbatch --time 2-0:00:00 -p gpuA100x4 --gres=gpu:1 -c 16 --mem 60000M --account=bbjs-delta-gpu run.sh
```

To use a whole node with multiple gpus, you can use
```bash
sbatch -n 4 -N 1 --time 48:00:00 -p gpuA40x4 --gres=gpu:4 -c 64 --mem 240000M --account=bbjs-delta-gpu run.sh
```
3. (debug usage)
You can submit interactive jobs for debugging purpose. Note that you can only have up to 1-hour for an interactive session. An example command is as follows:
```bash
srun -N 1 -n 1 -p gpuA40x4-interactive  --gres=gpu:1 -c 16 --mem 60000M --account=bbjs-delta-gpu --pty bash -
```

## ESPnet I/O Issue Fix

Delta will ocassionally have issues with file I/O, randomly preventing files from being accessed programmatically and causing training runs to crash. A simple fix is to catch the I/O exception and re-try. Issues with `sound` files for example, can be fixed by modifying [the sound reader](https://github.com/espnet/espnet/blob/master/espnet2/fileio/sound_scp.py#L29) into the following:


```
# the below code should replace the following: with soundfile.SoundFile(wav) as f: 

try:
  f = soundfile.SoundFile(wav)
except:
  time.sleep(5)
  f = soundfile.SoundFile(wav)
```
