# Nvidia Jetson Monitor

This is a repository for measuring and reporting temperatures and voltage, current and power consumption of different subsystems of Nvidia Jetson devices.

Currently there is support for the following devices:
* Jetson Orin Nano
* Jetson Orin AGX

And for the following metrics:
* Thermal sensors for available subsystems
    * CPU
    * GPU
    * SOC
* Power, voltage and current for:
    * CPU
    * GPU
    * SOC
    * CV
    * VDD

You can select what is reported with the `--metrics` and `--subsystems` params.

## How to run

```bash
pip install -r requirements.txt
cd src/
python main.py --help


usage: main.py [-h] [--metrics {current,voltage,power,temps,all} [{current,voltage,power,temps,all} ...]] [--subsystems {cpu,gpu,soc,all,CPU,GPU,SOC} [{cpu,gpu,soc,all,CPU,GPU,SOC} ...]]
               [--device {orin_agx,orin_nano}] [--dummy] [--log-redis] [--redis-stream REDIS_STREAM] [--max-iterations MAX_ITERATIONS]

Jetson Monitor Tool

options:
  -h, --help            show this help message and exit
  --metrics {current,voltage,power,temps,all} [{current,voltage,power,temps,all} ...]
                        metric(s) to report on
  --subsystems {cpu,gpu,soc,all,CPU,GPU,SOC} [{cpu,gpu,soc,all,CPU,GPU,SOC} ...]
                        subsystem(s) to report metrics on
  --device {orin_agx,orin_nano}
                        Device to measure on (Orin AGX, Orin Nano)
  --dummy               Emulate filesystem
  --log-redis           Use redis for logging
  --redis-stream REDIS_STREAM
                        Name of redis stream.
  --max-iterations MAX_ITERATIONS
                        Max number of iterations to schedule
```

## Testing locally

To test locally, we fake the filesystem structure (`--dummy` flag), so that we don't need the actual Jetson devices in the filesystem.

## Running on Jetson

To run on Jetson, you may need `sudo` rights for altering/accessing some of the metrics.

## Requirements

To support redis logging, we need redis >= 5.0 for streams support.

## Contact

For questions about the repo, please reach out to [@stevelaskaridis](https://github.com/stevelaskaridis).