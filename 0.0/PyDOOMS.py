"""
Module providing the PyDOOMS API as well as the superclass for all shared objects when using PyDOOMS
"""

from ObjectStore import *
from Communication import *

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
        time.sleep(0.001)
        get(id)


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


_store = ObjectStore()
_comm = Communication(_store)
