"""
A basic monte-carlo implementation for calculating pi.
Assumes the argument supplied to the nodes is the node ID, starting from 0

Node 0 creates the shared objects and sums the result,
all other nodes fetches the objects and each processes will work on one object each
"""

import random, math, sys, os, time, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Board import Board
import PyDOOMS


# Worker function
def worker(workerID, myDarts):
    start = time.time()

    if (workerID == 0):
        for boardID in range(PyDOOMS.getNumOfWorkers()):
            Board(boardID)

    PyDOOMS.barrier()
    board = PyDOOMS.get(workerID)

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
    if (workerID == 0):
        pi = 0.0
        i = 0
        while i < PyDOOMS.getNumOfWorkers():
            b = PyDOOMS.get(i)
            if b.ready:
                pi = pi + b.calc_pi()
                i = i + 1
            else:
                logging.critical("Board: " + str(i) + " - " + str(b.ready))
                time.sleep(1)

        #logging.debug("Pi: " + str(pi / PyDOOMS.getNumOfWorkers()) + " calculated in " + str(time.time() - start) + " seconds.")
        print str(time.time() - start)

    #logging.debug("Worker: " + str(workerID) + " dead. Worked for " + str(time.time() - start) + " seconds.")



darts = 4000000 / PyDOOMS.getNumOfWorkers()

PyDOOMS.execute(worker, darts)

