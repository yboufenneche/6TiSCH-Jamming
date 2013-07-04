#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Topology')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import random

import Propagation
import Mote
from SimSettings import SimSettings as s

class Topology(object):
    
     #======================== singleton pattern ===============================
    
    _instance      = None
    _init          = False
    
    RANDOM         = "RANDOM"
    FULL_MESH      = "FULL_MESH"
    BINARY_TREE    = "BINARY_TREE"
    LINE           = "LINE"
    LATTICE        = "LATTICE"
    MIN_DISTANCE   = "MIN_DISTANCE"
    
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Topology,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # store params
        
        # variables
        self.dataLock            = threading.Lock()
        self.motes=[Mote.Mote(id) for id in range(s().numMotes)]
         
    def createTopology(self,type):
          # set the mote's traffic goals
        if type == self.RANDOM:
             self._createRandomTopology()
        elif type == self.FULL_MESH:
            #make sure that the traffic requirements can be met with that so demanding topology.
            self._createFullMeshTopology()   
        elif type == self.BINARY_TREE:
            self._createBTreeTopology()
        elif type == self.LINE:
            raise NotImplementedError('Mode {0} not implemented'.format(type))         
        elif type == self.LATTICE:
            raise NotImplementedError('Mode {0} not implemented'.format(type))
        elif type == self.MIN_DISTANCE:
            raise NotImplementedError('Mode {0} not implemented'.format(type))
        else: 
            raise NotImplementedError('Mode {0} not supported'.format(type))
                
        return self.motes
    
    def _createRandomTopology(self):
        for id in range(len(self.motes)):
            neighborId = None
            #pick a random neighbor
            while (neighborId==None) or (neighborId==id):
                neighborId = random.randint(0,len(self.motes)-1)
            #initialize the traffic pattern with that neighbor    
            self.motes[id].setDataEngine(
                self.motes[neighborId],
                s().traffic,
            )
            
    def _createFullMeshTopology(self):
        for id in range(len(self.motes)):
            for nei in range(len(self.motes)):
                if nei!=id:
                    #initialize the traffic pattern with that neighbor
                    self.motes[id].setDataEngine(
                        self.motes[nei],
                        s().traffic,
                    )
                    

    def _addChild(self, id,child):
        print 'i {0}'.format(id)
        #downstream link
        self.motes[id].setDataEngine(self.motes[child], s().traffic)
        #upstream link
        self.motes[child].setDataEngine(self.motes[id], s().traffic)

    def _createBTreeTopology(self):
        print 'len {0}, {1}'.format(len(self.motes),(len(self.motes)/2))
        for id in range((len(self.motes)/2)):
              self._addChild(id,(2*id) + 1)
              print 'child 1 {0}'.format((2*id)+1)
              #check if it has second child
              if (2*(id+1)<len(self.motes)):
                  #other child
                  self._addChild(id,2*(id+1))
                  print 'child 2 {0}'.format(2*(id+1))
            
            
            