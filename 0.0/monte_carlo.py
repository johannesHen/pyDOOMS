import PyDOOMS
from Board import Board
import random, math, time, sys


# SETUP
start = time.time()
myname = eval(sys.argv[1])

darts = 20000
totalClients = 4

darts = darts / totalClients

if myname == 0:
    Board(0)
    Board(1)
    Board(2)
    Board(3)


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

PyDOOMS.comm.addOutgoingUpdate(board.ID, "hits", board.hits)
PyDOOMS.comm.addOutgoingUpdate(board.ID, "darts", board.darts)
PyDOOMS.comm.addOutgoingUpdate(board.ID, "ready", board.ready)

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
            print "board ",i,":",b.ready
            time.sleep(1)

    print "Pi: " + str(pi / totalClients) + " calculated in",time.time() - start

else:
    print "Client",myname," dead. Worked for",time.time() - start, "seconds."

PyDOOMS.shutdown()

