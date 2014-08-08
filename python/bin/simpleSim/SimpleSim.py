#!/usr/bin/python

'''
 @authors:
       Thomas Watteyne    <watteyne@eecs.berkeley.edu>    
       Xavier Vilajosana  <xvilajosana@uoc.edu> 
                          <xvilajosana@eecs.berkeley.edu>
'''

import os
import sys
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SimpleSim')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import logging.config

from optparse      import OptionParser

from SimEngine     import SimEngine, \
                          SimSettings
                          
from SimGui        import SimGui

#============================ defines =========================================

#============================ main ============================================

def parseCliOptions():
    
    parser = OptionParser()
    
    parser.add_option( '--nm',
        dest       = 'numMotes',
        type       = 'int',
        default    = 10,
        help       = 'Number of motes',
    )
    
    # not used
    parser.add_option( '-d',
        dest       = 'degree',
        type       = 'int',
        default    = 1,
        help       = 'Not used.',
    )
    
    parser.add_option( '-c',
        dest       = 'channels',
        type       = 'int',
        default    = 16,
        help       = 'Number of channel (between 1 and 16)',
    )
    
    parser.add_option( '--ts',
        dest       = 'timeslots',
        type       = 'int',
        default    = 101,
        help       = 'Number of timeslots per slotframe',
    )
    
    parser.add_option( '--traffic',
        dest       = 'traffic',
        type       = 'float',
        default    = 0.1,
        help       = 'Average delay, in s, between two packets generated by a mote',
    )
    
    parser.add_option( '--trafficSTD',
        dest       = 'trafficSTD',
        type       = 'float',
        default    = 0.1,
        help       = 'Variability of the traffic, in [0..1[. 0 for CBR.',
    )
    
    # not used
    parser.add_option( '--op',
        dest       = 'overprovisioning',
        type       = 'float',
        default    = 1.0,
        help       = 'Not used.',
    )

    # a side of area in km (This can be treated as cm when plotted)
    parser.add_option( '--side',
        dest       = 'side',
        type       = 'float',
        default    = 1.0, 
        help       = 'Side of the square deployment area, in km.',
    )
    
    # Threshold used by OTF for limitating cells allocation
    parser.add_option( '--OTFthresh',
        dest       = 'OTFthresh',
        type       = 'int',
        default    = 0, 
        help       = 'OTF threshhold, see draft, in cells.',
    )
    
    # Run number
    parser.add_option( '--runs',
        dest       = 'maxRunNum',
        type       = 'int',
        default    = 1000, 
        help       = 'Number of simulation runs.',
    )
    
    # Cycle number
    parser.add_option( '--cycles',
        dest       = 'cycleEnd',
        type       = 'int',
        default    = 100, 
        help       = 'Duration of one simulation run, in slotframe cycle.',
    )
    
    (opts, args)  = parser.parse_args()
    
    return opts.__dict__

def main():
    
    logging.config.fileConfig('logging.conf')
    
    # retrieve the command line args
    args      = parseCliOptions()
    
    # instantiate a SimSettings
    settings  = SimSettings.SimSettings()
    for (k,v) in args.items():
        # v=eval(v)
        # if type(v) is 'float' and (v<0 or v>1):
        #     v=0.1
        # elif type(v) is 'list':
        #     print v
        setattr(settings,k,v)
    
    # For multiple runs of simulation w/o GUI
    #'''
    gui = None
    for runNum in xrange(settings.maxRunNum):
        # instantiate a SimEngine object
        print('start run num: {0}\n'.format(runNum))
        if not gui:
            gui       = SimGui.SimGui()
        simengine = SimEngine.SimEngine()
        simengine.join()
        SimEngine.SimEngine.setCount()
        simengine._instance      = None
        simengine._init          = False
        print('end run num: {0}\n'.format(runNum))    
    
    #'''
    
    # For single run with GUI
    '''
    simengine = SimEngine.SimEngine() 
    # instantiate the GUI interface
    gui       = SimGui.SimGui()
    '''
    
if __name__=="__main__":
    main()
