from ObjectStore import *
from Communication import *

class SharedObject(object):
    """
    Class to be subclassed by all objects to be shared with other nodes
    """

    ID = None

    def __init__(self, id):
        self.ID = id
        store.addObject(self)
        comm.spreadObject(self)


    def update(self, name, value):
        self.__dict__[name] = value



def get(id):
    obj = store.objects[id][0]
    if (obj is not None):
        return obj
    else:
        raise Exception('Object not found')

def barrier():
    comm.comm_barrier()

def shutdown():
    comm.commShutdown()


store = ObjectStore()
comm = Communication(store)
