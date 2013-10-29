import SharedObject
import random, math, time, sys

class Board(SharedObject.SharedObject):
    """
    Class representing a board
    """
    def __init__(self, ID):
        SharedObject.SharedObject.__init__(self, ID)
        self.hits = 0
        self.darts = 0
        self.ready = False

    def hit(self):
        self.hits = self.hits + 1
        self.darts = self.darts + 1

    def miss(self):
        self.darts = self.darts + 1

    def calc_pi(self):
        return (4.0 * self.hits) / self.darts



# SETUP
start = time.time()
myname = eval(sys.argv[1])

darts = 2000000
totalClients = 4

darts = darts / totalClients

board = Board(myname)

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

SharedObject.manager.comm.addOutgoingUpdate(board.ID, "hits", board.hits)
SharedObject.manager.comm.addOutgoingUpdate(board.ID, "darts", board.darts)
SharedObject.manager.comm.addOutgoingUpdate(board.ID, "ready", board.ready)

SharedObject.barrier()



# Sum result
pi = 0.0

if myname == 0:
    i = 0
    while i < totalClients:
        b = SharedObject.get(i)
        if b.ready:
            pi = pi + b.calc_pi()
            i = i + 1
        else:
            print "board ",i,":",b.ready
            time.sleep(1)

    print "Pi: " + str(pi / totalClients) + " calculated in",time.time() - start

else:
    time.sleep(1)
    print "Client",myname," dead. Worked for",time.time() - start, "seconds."