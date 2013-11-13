"""
Module providing the PyDOOMS API as well as the superclass for all shared objects when using PyDOOMS
"""

import sys
from ObjectStore import *
from Communication import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d (%(threadName)-2s) %(message)s',datefmt='%M:%S'
                   )

class SharedObject(object):
    """
    Superclass for all shared objects.
    """

    ID = None

    def __init__(self, id):
        """
        Initializes an object by adding it to the object store
        as well as sending it to all other nodes
        """
        self.ID = id
        _store.addObject(self)
        _comm.spreadObject(self)


    def update(self, name, value):
        """
        Sets an attribute in this object to the new value
        Called when receiving updates from other nodes
        """
        self.__dict__[name] = value
        _store.addObject(self)


def get(id):
    """
    Returns the object with id id from the object store if it can be found
    """
    try:
        obj = _store.objects[id]
        if (obj is not None):
            return obj
        else:
            raise Exception('Object not found')
    except KeyError:
        time.sleep(0.0001)
        logging.debug("No matching object found, trying again...")
        return get(id)


def barrier():
    """
    Triggers a barrier synchronization among all nodes
    """
    _comm.commBarrier()


def shutdown():
    """
    Gracefully shuts down the communicating MPI thread
    """
    _comm.commShutdown()


def getNodeID():
    """
    Return the ID of this node. Set at startup with command line argument
    """
    return nodeID


def _reset():
    """
    Reset the object store and communication thread states.
    Only used for testing
    """
    _comm.reset()


nodeID = eval(sys.argv[1])

_store = ObjectStore()
_comm = Communication(_store)
