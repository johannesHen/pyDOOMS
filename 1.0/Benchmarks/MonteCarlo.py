"""
A basic monte-carlo implementation for calculating pi.

Node 0 creates the shared objects and sums the result,
all other nodes fetches the objects and each worker will work on one object each
"""

import random, math, sys, os, time, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Board import Board
import PyDOOMS


# Worker function
def monteCarlo(workerID, myDarts):

    if (workerID == 0):
        for boardID in range(PyDOOMS.getNumberOfWorkers()):
            Board(boardID)

    PyDOOMS.barrier()

    start = time.time()
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

    PyDOOMS.objectUpdated(board, "hits")
    PyDOOMS.objectUpdated(board, "darts")
    PyDOOMS.objectUpdated(board, "ready")


    PyDOOMS.barrier()

    # Sum result
    if (workerID == 0):
        pi = 0.0
        i = 0
        while i < PyDOOMS.getNumberOfWorkers():
            b = PyDOOMS.get(i)
            if b.ready:
                pi = pi + b.calc_pi()
                i = i + 1
            else:
                logging.critical("Board: " + str(i) + " - " + str(b.ready))
                time.sleep(1)

        logging.info("Pi: " + str(pi / PyDOOMS.getNumberOfWorkers()) + " calculated in " + str(time.time() - start) + " seconds.")

    logging.info("Worker: " + str(workerID) + " dead. Worked for " + str(time.time() - start) + " seconds.")



darts = 4000000 / PyDOOMS.getNumberOfWorkers()

PyDOOMS.execute(monteCarlo, darts)

