from ObjectStore import *
from Communication import *

class SharedObject(object):
    """
    Superclass for all shared objects.
    """

    ID = None

    def __init__(self, id):
        self.ID = id
        _store.addObject(self)
        _comm.spreadObject(self)


    def update(self, name, value):
        self.__dict__[name] = value


def get(id):
    obj = _store.objects[id][0]
    if (obj is not None):
        return obj
    else:
        raise Exception('Object not found')

def barrier():
    _comm.comm_barrier()

def shutdown():
    _comm.commShutdown()


_store = ObjectStore()
_comm = Communication(_store)
