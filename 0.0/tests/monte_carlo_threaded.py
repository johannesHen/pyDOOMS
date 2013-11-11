"""
A basic monte-carlo implementation for calculating pi.
Assumes the argument supplied to the nodes is the node ID, starting from 0

Node 0 creates the shared objects and sums the result,
all other nodes fetches the objects and work on one object each
"""

import random, math, sys, os, time, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import threading
import PyDOOMS
from Board import Board


# SETUP
start = time.time()
myname = eval(sys.argv[1])
numberOfClients = eval(sys.argv[2])
threadsPerNode = eval(sys.argv[3])

darts = 4000000
totalClients = numberOfClients*threadsPerNode

darts = darts / totalClients


# Worker function
def worker(workerID, myDarts):
    if (myname == 0 and workerID == 0):
            for boardID in range(totalClients):
                Board(boardID)

    PyDOOMS.barrier()
    board = PyDOOMS.get(myname*threadsPerNode+workerID)

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

    PyDOOMS._comm.addOutgoingUpdate(board.ID, "hits", board.hits)
    PyDOOMS._comm.addOutgoingUpdate(board.ID, "darts", board.darts)
    PyDOOMS._comm.addOutgoingUpdate(board.ID, "ready", board.ready)

    PyDOOMS.barrier()


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


# Start workers
workerThreads = []
for i in range(threadsPerNode):
    t = threading.Thread(target=worker, args=(i,darts))
    workerThreads.append(t)
    t.start()

# Wait for workers to finish
for threads in workerThreads:
    t.join()

# Shut down commThread and quit
PyDOOMS.shutdown()


