"""
A basic monte-carlo implementation for calculating pi.
Assumes the argument supplied to the nodes is the node ID, starting from 0

Node 0 creates the shared objects and sums the result,
all other nodes fetches the objects and work on one object each
"""

import PyDOOMS
from Board import Board
import random, math, time, sys


# SETUP
start = time.time()
myname = eval(sys.argv[1])
numberOfClients = eval(sys.argv[2])

darts = 4
totalClients = numberOfClients

darts = darts / totalClients

if myname == 0:
    for boardID in range(totalClients):
        Board(boardID)

    #Board(0)
    #Board(1)
    #Board(2)
    #Board(3)


PyDOOMS.barrier()
board = PyDOOMS.get(myname)

# Compute
while (darts > 0):

    x = random.random()
    y = random.random()
    dist = math.sqrt((x*x)+(y*y))
    if (dist <= 1.0):
        board.hit()
    else:
        board.miss()

    darts = darts - 1
board.ready = True

PyDOOMS._comm.addOutgoingUpdate(board.ID, "hits", board.hits)
PyDOOMS._comm.addOutgoingUpdate(board.ID, "darts", board.darts)
PyDOOMS._comm.addOutgoingUpdate(board.ID, "ready", board.ready)

PyDOOMS.barrier()


# Sum result
pi = 0.0

if myname == 0:
    i = 0
    while i < totalClients:
        b = PyDOOMS.get(i)
        if b.ready:
            pi = pi + b.calc_pi()
            i = i + 1
        else:
            #print "board ",i,":",b.ready
            time.sleep(1)

    print time.time() - start
    #print "Pi: " + str(pi / totalClients) + " calculated in",time.time() - start

else:
    #print "Client",myname," dead. Worked for",time.time() - start, "seconds."
    pass

PyDOOMS.shutdown()
