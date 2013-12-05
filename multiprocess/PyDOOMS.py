"""
Module providing the PyDOOMS API as well as the superclass for all shared objects when using PyDOOMS
"""

import sys, os, time
from datetime import datetime
from ObjectStore import *
from Communication import *
from multiprocessing import Process, Manager


# Setup logging
path = os.path.abspath(os.path.dirname(__file__))
logDir = os.path.join(path,'logs')

if not os.path.exists(logDir):
    try:
        os.makedirs(logDir)
    except OSError:
        pass
        # If several nodes run on the same system
        # only one will successfully create a directory,
        # the rest will raise OSError

logging.basicConfig(filename=logDir + '/' + str(os.path.split(sys.argv[0][:-3])[1]) + "_" + str(datetime.now())+ '.log',
                    level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d (%(threadName)-2s) %(message)s',
                    datefmt='%M:%S')


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
        The updated object is added to the object store so that the SyncManager
        can see the changes and spread them to other local workers.
        """
        self.__dict__[name] = value
        _store.addObject(self)



class SharedObjectError(Exception):
    """
    PyDOOMS exception for shared objects
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



def get(id):
    """
    Returns the object with id id from the object store if it can be found
    """
    try:
        obj = _store.objects[id]
        if (obj is not None):
            return obj
        else:
            raise SharedObjectError('Shared object with ID: ' + str(id) + ' is None')
    except KeyError:
        time.sleep(0.0001)
        try:
            return get(id)
        except RuntimeError:
            raise SharedObjectError('No shared object with ID: ' + str(id) + ' found')



def execute(worker, *workerArgs):
    """
    Initialize the local object store shared between processes, spawn worker processes,
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


def shutdown():
    """
    Gracefully shuts down the communicating MPI thread
    """
    _comm.commShutdown()


def getNodeID():
    """
    Return the ID of this node. The same as the MPI rank for this node.
    Returns None if called before PyDOOMS.execute() since the MPI communication has not yet been initialized
    """
    return nodeID


def getNumberOfNodes():
    """
    Return number of nodes running pyDOOMS in the network. Set at startup with command line argument
    """
    return numberOfNodes


def getNumberOfWorkers():
    """
    The total number of workers in the cluster. workersPerNode is set at startup with command line argument
    """
    return numberOfNodes*workersPerNode


def _start(worker, workerArgs, p):
    """
    Set pipe p as the pipe to use in this worker process for receiving messages from the CommThread,
    and starts executing the worker function
    """
    _comm.receivePipe = p

    worker(*workerArgs)


def _reset():
    """
    Reset the object store.
    Only used for testing
    """
    _store.objects.clear()


nodeID = None
numberOfNodes = eval(sys.argv[1])
workersPerNode = eval(sys.argv[2])

_comm = None
_store = None
