"""
A basic monte-carlo implementation for calculating pi.
Assumes the argument supplied to the nodes is the node ID, starting from 0

Node 0 creates the shared objects and sums the result,
all other nodes fetches the objects and each processes will work on one object each
"""

import random, math, sys, os, time, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from multiprocessing import Process, Manager
from Board import Board
import PyDOOMS


# SETUP
start = time.time()
myname = PyDOOMS.getNodeID()
numberOfClients = eval(sys.argv[2])
procsPerNode = eval(sys.argv[3])

darts = 4000000
totalClients = numberOfClients*procsPerNode

darts = darts / totalClients



# Worker function
def worker(workerID, myDarts):
    if (myname == 0 and workerID == 0):
            for boardID in range(totalClients):
                b = Board(boardID)
                #logging.debug("Node: " + str(myname) + "_" + str(workerID) +  " created board " + str(boardID) + " with darts: " + str(b.hits))

    #logging.debug("Node: " + str(myname) + "_" + str(workerID) +  " entering barrier")
    PyDOOMS.barrier()
    #logging.debug("Node: " + str(myname) + "_" + str(workerID) +  " exiting barrier")
    board = PyDOOMS.get(myname*procsPerNode+workerID)

    # Compute
    while (myDarts > 0):
        x = random.random()
        y = random.random()
        dist = math.sqrt((x*x)+(y*y))
        if (dist <= 1.0):
            board.hit()
        else:
            board.miss()

        myDarts = myDarts - 1
    board.ready = True

    PyDOOMS._store.addObject(board) # Manager.dict bug makes changes in objects in the dict not written to dict
    PyDOOMS._comm.addOutgoingUpdate(board.ID, "hits", board.hits)
    PyDOOMS._comm.addOutgoingUpdate(board.ID, "darts", board.darts)
    PyDOOMS._comm.addOutgoingUpdate(board.ID, "ready", board.ready)


    #logging.debug("Node: " + str(myname) + "_" + str(workerID) +  " entering second barrier")
    PyDOOMS.barrier()
    #logging.debug("Node: " + str(myname) + "_" + str(workerID) +  " exiting second barrier")

    # Sum result
    pi = 0.0

    if (myname == 0 and workerID == 0):
        i = 0
        while i < totalClients:
            b = PyDOOMS.get(i)
            if b.ready:
                pi = pi + b.calc_pi()
                i = i + 1
            else:
                print "board ",i,":",b.ready
                time.sleep(1)

        logging.debug("Pi: " + str(pi / totalClients) + " calculated in " + str(time.time() - start) + " seconds.")

    logging.debug("Worker: " + str(myname) + "_" + str(workerID) + " dead. Worked for " + str(time.time() - start) + " seconds.")



# Setup multiprocessing objectStore dictionary
PyDOOMS._store.setDictionary(Manager().dict())

# Start workers
workerProcs = []
for i in range(procsPerNode):
    p = Process(target=worker, args=(i,darts))
    workerProcs.append(p)
    p.start()

# Wait for workers to finish
for p in workerProcs:
    p.join()

# Shut down commThread and quit
PyDOOMS.shutdown()


