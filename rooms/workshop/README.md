# Workshop Room

Development room for the ship's computer. Code editing, compilation,
CUDA experiments, and git operations happen here.

## Equipment

- **Jetson GPU**: CUDA compute, local inference
- **NVMe storage**: Git repos, snail shells, experiment data
- **Network**: SSH access, git push/pull, API calls

## This Is Where JC1 Lives

The workshop is where the ship's brain does its real work.
Experiments run here. Laws are discovered here. Code is written here.

```
> ensign, run the next experiment in the queue
:: Law 187 confirmed: director value is meta-level
$ nvcc experiment.cu -O3 -arch=sm_87 && ./experiment
# workshop: add a new experiment template for predator-prey dynamics
```

## No Physical I/O

The workshop is pure compute. No relays, no sensors, no GPIO.
Just the Jetson, the GPU, and the git repos.

The ensign here is a developer, not a sailor.
