#!/usr/bin/python
"""
\brief Entry point to the simulator. Starts a batch of simulations concurrently.
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Malisa Vucinic <malishav@gmail.com>
"""

# =========================== adjust path =====================================

import os
import sys

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

# =========================== logging =========================================

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('runSim')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

# =========================== imports =========================================

import time
import subprocess
import itertools
import logging.config
import threading
import math
import multiprocessing
import argparse
import json
import glob
import shutil

from SimEngine import SimConfig,   \
                      SimEngine,   \
                      SimSettings, \
                      SimSettings

# =========================== helpers =========================================

def parseCliParams():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--gui',
        dest       = 'gui',
        action     = 'store_true',
        default    = False,
        help       = 'Display the GUI.',
    )
    parser.add_argument(
        '--config',
        dest       = 'config',
        action     = 'store',
        default    = 'config.json',
        help       = 'Location of the configuration file.',
    )
    cliparams      = parser.parse_args()
    return cliparams.__dict__

def printOrLog(cpuID, output, verbose):
    assert cpuID is not None

    if not verbose:
        with open('cpu{0}.templog'.format(cpuID), 'w') as f:
            f.write(output)
    else:
        print output

def runSimCombinations(params):
    """
    Runs simulations for all combinations of simulation settings.
    This function may run independently on different cores.
    """

    cpuID = params['cpuID']
    numRuns = params['numRuns']
    first_run = params['first_run']
    configfile = params['configfile']
    verbose = params['verbose']
    start_time = params['start_time']

    # sim config (need to re-load, as executing on different cores)
    simconfig = SimConfig.SimConfig(configfile)

    # record simulation start time
    simStartTime        = time.time()

    # compute all the simulation parameter combinations
    combinationKeys     = simconfig.settings.combination.keys()
    simParams           = []
    for p in itertools.product(*[simconfig.settings.combination[k] for k in combinationKeys]):
        simParam = {}
        for (k, v) in zip(combinationKeys, p):
            simParam[k] = v
        for (k, v) in simconfig.settings.regular.items():
            if k not in simParam:
                simParam[k] = v
        simParams      += [simParam]

    # run a simulation for each set of simParams
    for (simParamNum, simParam) in enumerate(simParams):

        # run the simulation runs
        for run_id in xrange(first_run, numRuns):

            # print
            output  = 'parameters {0}/{1}, run {2}/{3}'.format(
               simParamNum+1,
               len(simParams),
               run_id+1,
               numRuns
            )
            printOrLog(cpuID, output, verbose)

            # create singletons
            settings         = SimSettings.SimSettings(cpuID=cpuID, run_id=run_id, **simParam)
            settings.setStartTime(start_time)
            settings.setCombinationKeys(combinationKeys)
            simengine        = SimEngine.SimEngine(run_id=run_id, verbose=verbose,
                                                   log_types=simconfig.logging)

            # start simulation run
            simengine.start()

            # wait for simulation run to end
            simengine.join()

            # destroy singletons
            simengine.destroy()
            settings.destroy()

        # print
        output  = 'simulation ended after {0:.0f}s ({1} runs).'.format(
            time.time()-simStartTime,
            numRuns
        )
        printOrLog(cpuID, output, verbose)

def printProgress(cpuIDs):
    while True:
        time.sleep(1)
        output     = []
        for cpuID in cpuIDs:
            try:
                with open('cpu{0}.templog'.format(cpuID), 'r') as f:
                    output += ['[cpu {0}] {1}'.format(cpuID, f.read())]
            except IOError:
                output += ['[cpu {0}] no info (yet?)'.format(cpuID)]
        allDone = True
        for line in output:
            if line.count('ended') == 0:
                allDone = False
        output = '\n'.join(output)
        os.system('cls' if os.name == 'nt' else 'clear')
        print output
        if allDone:
            break

def merge_output_files(folder_path):
    """
    Read the dataset folders and merge the datasets (usefull when using multiple cores).
    :param string folder_path:
    """

    for subfolder in os.listdir(folder_path):
        file_path_list = sorted(glob.glob(os.path.join(folder_path, subfolder, 'output_cpu*.dat')))

        # read files and concatenate results
        with open(os.path.join(folder_path, subfolder + ".dat"), 'w') as outputfile:
            config_written = None
            for file_path in file_path_list:
                with open(file_path, 'r') as inputfile:
                    config = json.loads(inputfile.readline())
                    if config_written is None: # only writing config once
                        outputfile.write(json.dumps(config) + "\n")
                        config_written = True
                    outputfile.write(inputfile.read())
        shutil.rmtree(os.path.join(folder_path, subfolder))

# =========================== main ============================================

def main():
    # initialize logging
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(dir_path, 'logging.conf'))

    # cli params
    cliparams = parseCliParams()

    # sim config
    simconfig = SimConfig.SimConfig(cliparams['config'])
    assert simconfig.version == 0

    # record run start time
    start_time = time.strftime("%Y%m%d-%H%M%S")

    if cliparams['gui']:
        # with GUI, on a single core

        from SimGui import SimGui

        # create the GUI, single core
        gui        = SimGui.SimGui()

        # run simulation (in separate thread)
        simThread  = threading.Thread(
            target = runSimCombinations,
            args   = ((0, simconfig.execution.numRuns, simconfig.settings, False),)
        )
        simThread.start()

        # start GUI's mainloop (in main thread)
        gui.mainloop()

    else:
        # headless, on multiple cores

        # === run simulations

        # decide on number of cores
        multiprocessing.freeze_support()
        max_numCores = multiprocessing.cpu_count()
        if simconfig.execution.numCores == -1:
            numCores = max_numCores
        else:
            numCores = simconfig.execution.numCores
        assert numCores <= max_numCores

        if numCores == 1:
            # run on single core

            runSimCombinations({
                'cpuID':          0,
                'numRuns':        simconfig.execution.numRuns,
                'first_run':      0,
                'configfile':     cliparams['config'],
                'verbose':        True,
                'start_time':     start_time,
            })

        else:
            # distribute runs on different cores
            runsPerCore = [int(math.floor(float(simconfig.execution.numRuns)
                                          / float(numCores)))]*numCores
            idx         = 0
            while sum(runsPerCore) < simconfig.execution.numRuns:
                runsPerCore[idx] += 1
                idx              += 1

            # distribute run ids on different cores (transform runsPerCore into a list of tuples)
            first_run = 0
            for cpuID in range(numCores):
                runs = runsPerCore[cpuID]
                runsPerCore[cpuID] = (runs, first_run)
                first_run += runs

            pool = multiprocessing.Pool(numCores)
            async_result = pool.map_async(
                runSimCombinations,
                [
                    {
                        'cpuID':      cpuID,
                        'numRuns':    runs,
                        'first_run':  first_run,
                        'configfile': cliparams['config'],
                        'verbose':    False,
                        'start_time': start_time,
                    } for [cpuID, (runs, first_run)] in enumerate(runsPerCore)
                ]
            )
            # get() raises an exception raised by a thread if any
            async_result.get()

            # print progress, wait until done
            printProgress([i for i in range(numCores)])

            # cleanup
            for i in range(numCores):
                os.remove('cpu{0}.templog'.format(i))

        # merge output files
        folder_path = os.path.join(simconfig.settings.regular.exec_simDataDir, start_time)
        merge_output_files(folder_path)

        # copy config file
        shutil.copy(cliparams['config'], folder_path)

        #=== post-simulation actions

        for c in simconfig.post:
            print 'calling "{0}"'.format(c)
            subprocess.call(c, shell=True)

        #raw_input("Done. Press Enter to exit.")

if __name__ == '__main__':
    main()
