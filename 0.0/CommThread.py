import threading
import time
import logging
import Queue
from mpi4py import MPI

class CommThread(threading.Thread):
    """
    Thread used sending and receiving messages using MPI
    """

    SPREAD_OBJECT = 0
    SEND_UPDATE = 1
    BARRIER_START = 2
    BARRIER_DONE = 3
    BARRIER_SENDS_DONE = 4
    OUTGOING_UPDATE = 5

    comm = MPI.COMM_WORLD
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()

    outgoingUpdatesSize = 10

    outgoingUpdates = []
    incomingUpdates = []


    def __init__(self, comm, sQueue, rQueue):
        threading.Thread.__init__(self)
        self.communication = comm
        self.sendQueue = sQueue
        self.receiveQueue = rQueue
        self.barrierUp = False
        self.barrierAcks = self.size - 1

    def broadcast(self, msg, tag):
        for i in [x for x in range(self.size) if x != self.rank]:
            #logging.debug("Rank " + str(self.rank) + " broadcast to " + str(i))
            self.comm.send(msg, i, tag)

    def receiveObject(self, obj):
        self.communication.manager.addObject(obj)

    def sendUpdates(self):
        #logging.debug("OutgoingUpdates: " + str(self.outgoingUpdates))
        for update in self.outgoingUpdates:
            self.sendUpdate(update)
        self.outgoingUpdates = []

    def sendUpdate(self, update):
        #logging.debug("Process "+str(self.comm.rank) + " Sending update " + str(update))
        self.broadcast(update, self.SEND_UPDATE)

    def mergeUpdates(self):
        mergedUpdates = dict()
        mergedUpdatesList = []

        for update in reversed(self.outgoingUpdates):
            if (not mergedUpdates.has_key((update[0],update[1]))):
                mergedUpdates[(update[0], update[1])] = update[2]
                mergedUpdatesList.append((update[0], update[1], update[2]))

        self.outgoingUpdates = list(mergedUpdatesList)


    def receiveUpdate(self, id, attr, value):
        if (self.barrierUp):
            self.communication.manager.objects[id][0].update(attr,value)
        else:
            self.incomingUpdates.append((id, attr, value))


    def processUpdates(self):
        for upd in self.incomingUpdates:
            self.communication.manager.objects[upd[0]][0].update(upd[1], upd[2])

    def barrierStart(self):
        #logging.debug("Process "+str(self.comm.rank) + " Starting barrier")
        self.barrierUp = True
        self.barrierAcks -= (self.size - 1)
        self.mergeUpdates()
        #logging.debug("Process "+str(self.comm.rank) + " Sending outgoing updates")
        self.sendUpdates()
        #logging.debug("Process "+str(self.comm.rank) + " Sending barrier ack")
        self.broadcast(0, self.BARRIER_SENDS_DONE)
        #logging.debug("Process "+str(self.comm.rank) + " Processing updates")
        self.processUpdates()

        if (self.barrierAcks == self.size - 1):
            self.barrierUp = False
            self.receiveQueue._put(self.BARRIER_DONE)

    def barrierAck(self):
        self.barrierAcks += 1
        if (self.barrierAcks == self.size - 1):
            self.barrierUp = False
            self.receiveQueue._put(self.BARRIER_DONE)

    def run(self):
        #logging.debug("Process " + str(self.communication.comm.rank) + " - New CommThread starting")

        while (True):
            try:
                (cmd, msg) = self.sendQueue.get(False)
                if (cmd == self.SPREAD_OBJECT):
                    #logging.debug("Process "+str(self.comm.rank) + " Spreading " + str(msg))
                    self.broadcast(msg, self.SPREAD_OBJECT)
                elif (cmd == self.BARRIER_START):
                    #logging.debug("Process "+str(self.comm.rank) + " Starting barrier")
                    self.barrierStart()
                elif (cmd == self.OUTGOING_UPDATE):
                    #logging.debug("Adding outgoing update:" + str(msg))
                    if (len(self.outgoingUpdates) >= self.outgoingUpdatesSize):
                        self.sendUpdate(self.outgoingUpdates[0])
                        self.outgoingUpdates.pop(0)
                    self.outgoingUpdates.append(msg)
            except Queue.Empty:
                if (self.comm.Iprobe(MPI.ANY_SOURCE, self.SPREAD_OBJECT)):
                    msg = self.comm.recv(source=MPI.ANY_SOURCE, tag=self.SPREAD_OBJECT)
                    self.receiveObject(msg)
                elif (self.comm.Iprobe(MPI.ANY_SOURCE, self.SEND_UPDATE)):
                    msg = self.comm.recv(source=MPI.ANY_SOURCE, tag=self.SEND_UPDATE)
                    self.receiveUpdate(*msg)
                elif (self.comm.Iprobe(MPI.ANY_SOURCE, self.BARRIER_SENDS_DONE)):
                    self.comm.recv(source=MPI.ANY_SOURCE, tag=self.BARRIER_SENDS_DONE)
                    self.barrierAck()

                time.sleep(0.0000001)