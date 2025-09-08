---
layout: post
title: Submit dependency jobs in SLURM
date: 2025-04-22 09:00:00-0800
description: dependency jobs in slurm
comments: false
---

## Submitting Dependency Jobs in SLURM

### Overview

When running computationally intensive tasks like speech recognition training in ESPnet, you may need to split your work into sequential jobs. SLURM's dependency feature allows you to create a chain of jobs where each job starts only after its predecessor completes successfully.

### What are Dependency Jobs?

Dependency jobs in SLURM are jobs that have a relationship with other jobs in the queue. The most common dependency type is `afterany`, which means a job will start only after the specified job has completed (regardless of the completion state).

### Automated Dependency Job Submission Script

The following script allows you to automatically submit multiple sequential jobs, with each job depending on the successful completion of the previous job. This is particularly useful for ESPnet experiments where you might find sbatch scripts in `exp/<exp_dir>/q/train.sh`.

```bash
#!/bin/bash

# Number of sequential jobs to submit
NUM_JOBS=5

# Ask user to paste their SLURM command
echo "Paste your SLURM command:"
read -r ORIGINAL_CMD

# Check if the command already contains a dependency flag
if [[ $ORIGINAL_CMD == *"--dependency"* ]]; then
  # Extract the existing dependency
  DEPENDENCY=$(echo $ORIGINAL_CMD | grep -o -- "--dependency=[^ ]*")
  # Remove the existing dependency to add our placeholder
  SBATCH_CMD=${ORIGINAL_CMD/$DEPENDENCY/DEPENDENCY_PLACEHOLDER}
else
  # Find the position after 'sbatch' to insert our dependency placeholder
  SBATCH_CMD=$(echo $ORIGINAL_CMD | sed 's/sbatch /sbatch DEPENDENCY_PLACEHOLDER /')
fi

# Submit the first job (with original dependency if it existed)
if [[ $ORIGINAL_CMD == *"--dependency"* ]]; then
  FIRST_CMD=${SBATCH_CMD/DEPENDENCY_PLACEHOLDER/$DEPENDENCY}
else
  # If no original dependency, the first job has no dependency
  FIRST_CMD=${SBATCH_CMD/DEPENDENCY_PLACEHOLDER/}
fi

job_id=$(eval "$FIRST_CMD" | grep -oP '(?<=Submitted batch job )\d+')
echo "Submitted job 1 with ID: $job_id"

# Submit the remaining jobs with dependencies on the previous job
for ((i=2; i<=NUM_JOBS; i++)); do
  next_cmd=${SBATCH_CMD/DEPENDENCY_PLACEHOLDER/--dependency=afterany:$job_id}
  job_id=$(eval "$next_cmd" | grep -oP '(?<=Submitted batch job )\d+')

  echo "Submitted job $i with ID: $job_id"
done
```

### How to Use This Script

1. Save the script above to a file (e.g., `submit_dependency_jobs.sh`)
2. Make it executable: `chmod +x submit_dependency_jobs.sh`
3. Run the script: `./submit_dependency_jobs.sh`
4. When prompted, paste your sbatch command (e.g., the command from ESPnet's `exp/<exp_dir>/q/train.sh`)
5. The script will submit the specified number of jobs in sequence, with each job depending on the completion of the previous one

### Key Features

- Handles cases where your original sbatch command already contains a dependency
- Preserves all original parameters of your sbatch command
- Provides feedback with job IDs as each job is submitted
- Customizable number of sequential jobs through the `NUM_JOBS` variable

### Common Dependency Types

While this script uses `afterany` (job starts after the previous job completes regardless of exit status), SLURM supports other dependency types:

- `after`: Start job after specified jobs have begun
- `afterok`: Start job only if specified jobs completed successfully
- `afternotok`: Start job only if specified jobs failed
- `aftercorr`: Start job after specified jobs have terminated with the same exit code

Modify the script as needed by changing `afterany` to your preferred dependency type.

### Other tips

You may also consider doing a sleep job for some interactive session (please keep it light). 

Use the following 
```bash
#!/usr/bin/env bash
#
# Reserve 1 GPU for up to 2 days by sleeping
#
#SBATCH --job-name=gpu_reserve
#SBATCH --output=gpu_reserve_%j.out
#SBATCH --error=gpu_reserve_%j.err

#SBATCH --export=PATH
#SBATCH -p ghx4
#SBATCH --gres=gpu:1
#SBATCH -c 32                         # 32 CPU cores
#SBATCH --mem=240000M                 # 240 GB RAM
#SBATCH --account=${ACCOUNT}
#SBATCH --time=2-0:00:00              # 2 days walltime

# Duration to sleep (in seconds). Override by passing a value when you sbatch:
#   sbatch reserve_gpu.sh 3600
DURATION=${1:-172800}

echo "[$(date)] Job $SLURM_JOB_ID on $SLURM_JOB_NODELIST: holding GPU for $DURATION seconds"
sleep "$DURATION"
echo "[$(date)] Job $SLURM_JOB_ID: done"
```

You can get the jobid from the above sbatch command.

Then execute `srun --jobid=$JOBID --pty /bin/bash`
