---
layout: post
title: Babel Usage
date: 2024-08-20 09:00:00-0800
description: Babel cluster usage.
comments: false
---

## Important Information
* Document: Babel is the cluster hosted in LTI, CMU. Besides this page, **please also check the [official document](https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Main_Page)**. You will need a CMU identity to access this document (i.e., andrew ID).
* Slack Channel: Babel users should join the `babel-babble` channel in `LTI` slack space to receive the latest information. You may also contact the cluster admin through that channel.
* Use Policy:
  * Generally, each user can use up to 8 GPUs without notifying the admin of the cluster.
  * Occasionally, one can use more than 8 GPUs but need to send a message in the slack channel to clarify the number of GPUs and the estimated time to finish. The admin will request you to lower your usage when the cluster is busy.
  * There is no charging mechanism in babel but please still use it reasonably.
* `swl_general` and `swl_short` partitions:
  * Nodes with names `babel-11-*` are former SWL cluster. Our lab members will have priority to these nodes as long as you use partitions `swl_general` and `swl_short`.


## Cluster Access
* Before you proceed, please make sure your access to Babel is approved by Prof. Shinji Watanabe.
  * Go to [LTI intranet](https://lti.cs.cmu.edu/misc-pages/intranet-forms.html) and then submit `HPC Cluster User Account Request Form`.
  * HPC Cluster Name: `babel`
  * Department Association: `LTI`
  * Faculty Sponsoring Account: `swatanab`
  * Additional Groups: `swl`
* Connect to the cluster by `ssh <username>@babel.lti.cs.cmu.edu`

## Login nodes, working nodes and working directories
* Once login, you will be in a `login` node. These nodes are used for login only and are not for real jobs.
* You jobs will be conducted by `working` nodes. You can allocate CPU/GPU resources for your jobs. Once allocated, you can also login these nodes from the login node by `ssh`. E.g., if there is a job running on `babel-11-29`, you can login that node by `ssh babel-11-29`.
* Working directories below are commonly used. Note `/data` is not visible to the `login` nodes.
  * Personal directory: `/data/user_data/<user_name>`
  * Shared corpus storage `/data/group_data/swl/corpora`
  * Legacy working directory of previous SWL user: `/data/group_data/swl/old_home`
  * Personal home, with very limited space. Do not use it for your works: `/home/<user_name>`


## Resource Allocation
* Resources in Babel are managed by `slurm`. For general use cases, please refer to [this document](https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Slurm)
* For ESPnet users, jobs are submitted to `slurm` automatically. 
  * For each recipe (e.g., `espnet/egs2/librispeech/asr1`), there are a `cmd.sh` and a `conf/slurm.conf` files. Setting `backend=slurm` in `cmd.sh` and setting `conf/slurm.conf` properly should be sufficient to use Babel resources. An example `conf/slurm.con` is below.
    ```
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
    option gpu=0 -p swl_general --mem 2000M
    option gpu=1 -p swl_general --gres=gpu:1 -c 8  --mem 30000M
    option gpu=2 -p swl_general --gres=gpu:2 -c 16 --mem 60000M
    option gpu=3 -p swl_general --gres=gpu:3 -c 24 --mem 90000M 
    option gpu=4 -p swl_general --gres=gpu:4 -c 32 --mem 120000M 
    option gpu=8 -p swl_general --gres=gpu:8 -c 48 --mem 240000M
    ```
    * Based on the number of GPUs you request, it will automatically select the setup above. E.g., if 2 GPUs are requested, configuration `gpu=2 -p swl_general --gres=gpu:2 -c 16 --mem 60000M` will be in use.
    * `-p swl_general` specify which `partition` the jobs are submitted to. Use `sinfo` to check all available partitions. Each partition will contain different resources. Members from `WavLab` will be able to use partitions `debug`, `general`, `long`, `cpu`, `swl_general` and `swl_short`.
    * `-c` means the CPU cores to allocate, usually 8 CPU cores for each GPU.
    * `--mem` means the CPU memory to allocate, usually 30G for each GPU.
    * Make sure `gpu=N` matches `--gres=gpu:N`
    * `default time=2-00:00:00` specify the estimated time of your jobs. The maximum valid time will be differnt based on the partition. Use `sinfo` to check that for each partition.
    * Your jobs will fail if the requested number of GPUs / CPU cores / memory beyond the possible configuration.
    * By adding `--exclude=<node>`, you can avoid submitting your jobs to certain nodes. E.g., `--exclude=babel-11-[13,29]`.
    * By adding `-w <nodes>`, you can submit your jobs to certain nodes, E.g., `--w babel-11-[13,29]`.
    * You can also specify the GPU types. E.g., to request A6000 GPUs, replace `--gres=gpu:4` to `--gres=gpu:A6000:4`.

## ESPnet
Using ESPnet on Babel will not cause extra difficulties. To setup the environment:
```
git clone https://github.com/espnet/espnet.git
cd espnet/tools
./setup_anaconda.sh <path-to-conda> <env_name> <python_version> # E.g., ./setup_anaconda.sh /data/user_data/<user_name>/tools/miniconda3 espnet 3.10
make TH_VERSION=<torch_version> CUDA_VERSION=<cuda_version> # E.g., make TH_VERSION=2.1.0 CUDA_VERSION=11.8
```
* Note: You will not need to use `module load` as before, as the conda will handle the CUDA automatically.

Then you can run ESPnet recipes. E.g.,
```
cd espnet/egs2/librispeech/asr1/
# configurate cmd.sh to use slurm backend
# configurate conf/slurm.conf as above
# Add your dataset path to db.sh
bash run.sh
```
Further ESPnet use guidance is beyond the scope of Babel. Readers can refer to the [tutorials](https://espnet.github.io/espnet/tutorial.html  ) in our [website](https://github.com/espnet/espnet).

## Misc.
* VSCode: Both login nodes and working nodes can be accessed by VSCode. Search `VSCode` in Babel official document for guidance.
* As `/data` directory is not visible to login nodes, one can keep a small CPU job for coding. Please only use a small amount of memory / CPU cores for this porpose. For short-time use, you can also allocate some GPUs, but please don't allocate GPUs for a long time for coding and debugging.

    ```
    sbatch --partition=swl_general --nodes=1 --tasks=1 --tasks-per-node=1 --cpus-per-task=4 --mem=8000M -w babel-11-17 --time=15-00:00:00 /home/<user_name>/run.sh & 

    ### with the run.sh example below
    #!/bin/bash
    sleep 15d
    ```
