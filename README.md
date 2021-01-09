# 6TiSCH-Jamming

Core Developers:

* Yassine Boufenneche (yboufenneche@usthb.dz)
* Rafik Zitouni (rafik.zitouni@ece.fr)
* Laurent George (laurent.george@esiee.fr)
* Nawel Gharbi (ngharbi@usthb.dz)

## Scope

6TiSCH is an IETF standardization working group that defines a complete protocol stack for ultra reliable ultra low-power wireless mesh networks.
This simulator implements the 6TiSCH protocol stack, exactly as it is standardized.
It allows you to measure the performance of a 6TiSCH network under different conditions.

Simulated protocol stack

|                                                                                                              |                                             |
|--------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| [RFC6550](https://tools.ietf.org/html/rfc6550), [RFC6552](https://tools.ietf.org/html/rfc6552)               | RPL, non-storing mode, OF0                  |
| [RFC6206](https://tools.ietf.org/html/rfc6206)                                                               | Trickle Algorithm                           |
| [draft-ietf-6lo-minimal-fragment-07](https://tools.ietf.org/html/draft-ietf-6lo-minimal-fragment-07)         | 6LoWPAN Fragment Forwarding                 |
| [RFC6282](https://tools.ietf.org/html/rfc6282), [RFC4944](https://tools.ietf.org/html/rfc4944)               | 6LoWPAN Fragmentation                       |
| [draft-ietf-6tisch-msf-10](https://tools.ietf.org/html/draft-ietf-6tisch-msf-10)                             | 6TiSCH Minimal Scheduling Function (MSF)    |
| [draft-ietf-6tisch-minimal-security-15](https://tools.ietf.org/html/draft-ietf-6tisch-minimal-security-15)   | Constrained Join Protocol (CoJP) for 6TiSCH |
| [RFC8480](https://tools.ietf.org/html/rfc8480)                                                               | 6TiSCH 6top Protocol (6P)                   |
| [RFC8180](https://tools.ietf.org/html/rfc8180)                                                               | Minimal 6TiSCH Configuration                |
| [IEEE802.15.4-2015](https://ieeexplore.ieee.org/document/7460875/)                                           | IEEE802.15.4 TSCH                           |

* connectivity models
    * Pister-hack
    * k7: trace-based connectivity
* miscellaneous
    * Energy Consumption model taken from
        * [A Realistic Energy Consumption Model for TSCH Networks](http://ieeexplore.ieee.org/xpl/login.jsp?tp=&arnumber=6627960&url=http%3A%2F%2Fieeexplore.ieee.org%2Fiel7%2F7361%2F4427201%2F06627960.pdf%3Farnumber%3D6627960). Xavier Vilajosana, Qin Wang, Fabien Chraim, Thomas Watteyne, Tengfei Chang, Kris Pister. IEEE Sensors, Vol. 14, No. 2, February 2014.
    
## Code Organization

* `SimEngine/`: the simulator
    * `Connectivity.py`: Simulates wireless connectivity.
    * `SimConfig.py`: The overall configuration of running a simulation campaign.
    * `SimEngine.py`: Event-driven simulation engine at the core of this simulator.
    * `SimLog.py`: Used to save the simulation logs.
    * `SimSettings.py`: The settings of a single simulation, part of a simulation campaign.
    * `Mote/`: Models a 6TiSCH mote running the different standards listed above.
* `bin/`: the scripts for you to run
* `gui/`: files for GUI (see "GUI" section for further information)
* `tests/`: the unit tests, run using `pytest`
* `traces/`: example `k7` connectivity traces

## Configuration

`runSim.py` reads `config.json` in the current working directory.
You can specify a specific `config.json` location with `--config` option.

```
python runSim.py --config=example.json
```

The `config` parameter can contain:

* the name of the configuration file in the current directory, e.g. `example.json`
* a path to a configuration file on the computer running the simulation, e.g. `c:\simulator\example.json`
* a URL of a configuration file somewhere on the Internet, e.g. `https://www.example.com/example.json`

### base format of the configuration file

```
{
    "version":               0,
    "execution": {
        "numCPUs":           1,
        "numRuns":           100
    },
    "settings": {
        "combination": {
            ...
        },
        "regular": {
            ...
        }
    },
    "logging":               "all",
    "log_directory_name":    "startTime",
    "post": [
        "python compute_kpis.py",
        "python plot.py"
    ]
}
```

* the configuration file is a valid JSON file
* `version` is the version of the configuration file format; only 0 for now.
* `execution` specifies the simulator's execution
    * `numCPUs` is the number of CPUs (CPU cores) to be used; `-1` means "all available cores"
    * `numRuns` is the number of runs per simulation parameter combination
* `settings` contains all the settings for running the simulation.
    * `combination` specifies variations of parameters
    * `regular` specifies the set of simulator parameters commonly used in a series of simulations
* `logging` specifies what kinds of logs are recorded; `"all"` or a list of log types
* `log_directory_name` specifies how sub-directories for log data are named: `"startTime"` or `"hostname"`
* `post` lists the post-processing commands to run after the end of the simulation.

See `bin/config.json` to find  what parameters should be set and how they are configured.