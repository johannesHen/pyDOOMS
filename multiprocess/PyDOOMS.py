"""
Module providing the PyDOOMS API as well as the superclass for all shared objects when using PyDOOMS
"""

import sys
from ObjectStore import *
from Communication import *
from multiprocessing import Process, Manager

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
        #logging.debug("No matching object found, trying again...")
        return get(id)



def execute(worker, *workerArgs):
    """
    Make the object store dictionary shared between processes, spawn worker processes,
    and shut down the mpi communication when all workers are done
    """

    # Initialize object store and communication thread
    global _store, _comm, nodeID

    _store = ObjectStore()
    _comm = Communication(_store, workersPerNode)

    while (not _comm.commThread.isAlive()):
            time.sleep(0.000001)
    nodeID = _comm.commThread.rank

    # Start workers
    workers = []
    for i in range(workersPerNode):
        argList = []
        for arg in reversed(workerArgs):
            argList.append(arg)
        p = Process(target=_start, args=(worker, (nodeID*workersPerNode+i,)+workerArgs, _comm.receivePipes[i][0]))
        workers.append(p)
        p.start()

    # Wait for workers to finish
    for p in workers:
        p.join()

    # Shut down commThread and quit
    shutdown()


def objectUpdated(obj, attr):
    """
    Adds the objects ID, attribute-name and value to an outgoing update
    """
    _comm.addOutgoingUpdate(obj.ID, attr, getattr(obj,attr))


def barrier():
    """
    Triggers a barrier synchronization among all nodes
    """
    _comm.commBarrier()


def _start(worker, workerArgs, p):
    """
    Sets the provided pipe as the pipe to use for receiving messages from the CommThread,
    and starts the worker
    """
    _comm.receivePipe = p

    worker(*workerArgs)


def shutdown():
    """
    Gracefully shuts down the communicating MPI thread
    """
    _comm.commShutdown()


def _reset():
    """
    Reset the object store and communication thread states.
    Only used for testing
    """
    _store.objects.clear()


def getNodeID():
    """
    Return the ID of this node. Set at startup with command line argument
    """
    return nodeID


def getNumOfWorkers():
    """
    The total number of workers in the cluster
    """
    return numberOfNodes*workersPerNode



nodeID = None
numberOfNodes = eval(sys.argv[1])
workersPerNode = eval(sys.argv[2])

_comm = None
_store = None
