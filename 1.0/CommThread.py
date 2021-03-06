from mpi4py import MPI
import threading
import Queue
import time
import logging


class CommThread(threading.Thread):
    """
    Thread handling all inter-node communication using MPI
    Intra-node communication is done using Queues.
    Also stores incoming and outgoing updates in lists of tuples on the form [(objectID, attr, value)]
    and merges updates before sending them.
    """

    SPREAD_OBJECT = 0
    SEND_UPDATE = 1
    BARRIER_START = 2
    BARRIER_DONE = 3
    BARRIER_SENDS_DONE = 4
    OUTGOING_UPDATE = 5
    SHUTDOWN = 6

    comm = MPI.COMM_WORLD
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()

    # The number of updates to keep until the next barrier.
    outgoingUpdatesBufferSize = 10


    def __init__(self, comm, workers, sQueue, rPipes):
        """
        Initialize the thread and setup local variables
        """
        threading.Thread.__init__(self)
        self.running = True

        self.outgoingUpdates = []
        self.incomingUpdates = []

        self.communication = comm
        self.sendQueue = sQueue
        self.receivePipes = rPipes
        self.workers = workers

        self.barrierUp = False
        self.barrierAcks = self.size - 1
        self.barrierStartRequests = 0

        self.currentSend = None


    def broadcast(self, msg, tag):
        """
        Sends message msg with tag tag to all nodes in the MPI.COMM_WORLD communicator
        except the local node
        """
        for i in [x for x in range(self.size) if x != self.rank]:
            #logging.debug("Node " + str(self.rank) + " broadcasting " + str(msg) + " to " + str(i))
            self.comm.send(msg, i, tag)


    def receiveObject(self, obj):
        """
        Adds the object obj to the local object store
        """
        self.communication.objStore.addObject(obj)


    def sendUpdates(self):
        """
        Broadcasts and removes all updates in self.outgoingUpdates
        """
        #logging.debug("OutgoingUpdates: " + str(self.outgoingUpdates))
        for update in self.outgoingUpdates:
            #logging.debug("Node " + str(self.rank) + " sending update")
            self.sendUpdate(update)
        self.outgoingUpdates = []


    def sendUpdate(self, update):
        """
        Broadcasts an update. An update is a 3-tuple of (objectID, attrName, attrValue).
        If a previously sent update has not been received,
        attempts to receive an incoming update to prevent deadlock while waiting.
        Also updates the object in the local object store with the updated value.
        """
        #logging.debug("Node "+str(self.comm.rank) + " Sending update " + str(update))
        self.communication.objStore.objects[update[0]].update(update[1], update[2])

        for i in [x for x in range(self.size) if x != self.rank]:
            #logging.debug("Node " + str(self.rank) + " broadcasting update")
            if self.currentSend is not None:

                while (not self.currentSend.Test()):
                    #logging.debug("Node " + str(self.rank) + " previous send not received, receiving updates instead")
                    if (self.comm.Iprobe(MPI.ANY_SOURCE, self.SEND_UPDATE)):
                        msg = self.comm.recv(source=MPI.ANY_SOURCE, tag=self.SEND_UPDATE)
                        self.receiveUpdate(*msg)
                    time.sleep(0.000001)

            self.currentSend = self.comm.isend(update, i, self.SEND_UPDATE)


    def mergeUpdates(self):
        """
        Attempts to merge updates in self.outgoingUpdates by removing duplicate id,attr entries with old values.
        self.outgoingUpdates is used as a FIFO-list so the last entry for a given objectID,attr pair
        contains the latest value.
        Ex:
        self.outgoingUpdates = [(id1,"attr1", value1),(id2,"attr1",value2),(id1,"attr1",value2)]
        calling mergedUpdates() will change the contents of self.outgoingUpdates to:
        self.outgoingUpdates = [(id2,"attr1",value2),(id1,"attr1",value2)]
        """
        mergedUpdates = dict()
        mergedUpdatesList = []

        for update in reversed(self.outgoingUpdates):
            if (not mergedUpdates.has_key((update[0],update[1]))):
                mergedUpdates[(update[0], update[1])] = update[2]
                mergedUpdatesList.append((update[0], update[1], update[2]))

        self.outgoingUpdates = list(mergedUpdatesList)


    def receiveUpdate(self, id, attr, value):
        """
        If currently in a barrier, this method updates the attribute attr to the new value value in the object with id id
        Otherwise, the update is appended to the list of incoming updates to be handled later
        """

        if (self.barrierUp):
            self.communication.objStore.objects[id].update(attr,value)
        else:
            self.incomingUpdates.append((id, attr, value))


    def processUpdates(self):
        """
        Applies all updates in self.incomingUpdates to the corresponding objects in the local object store
        """
        for upd in self.incomingUpdates:
            #logging.debug("Node: " + str(self.rank) + " processing update: " + str(upd))
            self.communication.objStore.objects[upd[0]].update(upd[1], upd[2])
        self.incomingUpdates = []


    def barrierStart(self):
        """
        Initialize barrier synchronization when all local workers has issued a request to start.
        Outgoing updates are merged before transmitted,
        and a broadcast is made to signal that all updates has been sent from this node.
        Finally, previously received updates are processed and the number of barrier acks received is checked
        to see if the barrier should finish.
        """
        #logging.debug("Node "+str(self.comm.rank) + " Barrier request")
        self.barrierStartRequests += 1

        if self.barrierStartRequests == self.workers:
            #logging.debug("Node "+str(self.comm.rank) + " Starting barrier")
            self.barrierUp = True
            self.barrierAcks -= (self.size - 1)
            self.mergeUpdates()
            #logging.debug("Node "+str(self.comm.rank) + " Sending outgoing updates")
            self.sendUpdates()
            #logging.debug("Node "+str(self.comm.rank) + " Sending barrier ack")
            self.broadcast(0, self.BARRIER_SENDS_DONE)
            #logging.debug("Node "+str(self.comm.rank) + " Processing updates")
            self.processUpdates()

            """
            If the thread has already received barrier done messages from all other nodes
            it wont receive any more and the check for completion must be done here
            """
            self.barrierDoneCheck()


    def barrierAck(self):
        """
        Increment the number of barrierAcks received and do a check if the barrier should finish.
        """
        self.barrierAcks += 1
        self.barrierDoneCheck()


    def barrierDoneCheck(self):
        """
        Check if all remote nodes in the MPI.COMM_WORLD communicator has sent a BARRIER_SENDS_DONE message.
        If True issue a MPI_barrier and exit the barrier by sending a BARRIER_DONE message to the local workers,
        to indicate that the barrier synchronization is done.
        """
        if (self.barrierAcks == self.size - 1):
            self.barrierStartRequests -= self.workers
            self.barrierUp = False
            self.comm.barrier()
            for i in range(self.workers):
                self.receivePipes[i][1].send(self.BARRIER_DONE)


    def run(self):
        """
        The thread's run loop. Used to send or otherwise handle messages received
        from the local workers and to receive and handle messages from remote nodes.
        Commands and messages from the local workers has top priority for handling, receives are handled
        secondarily, and when no message are sent or received the thread sleeps.
        """

        #logging.debug("Node " + str(self.rank) + " - New CommThread starting")
        while (self.running):
            try:
                try:
                    (cmd, msg) = self.sendQueue.get(False)

                    if (cmd == self.SPREAD_OBJECT):
                        #logging.debug("Node "+str(self.comm.rank) + " Spreading " + str(msg))
                        self.broadcast(msg, self.SPREAD_OBJECT)

                    elif (cmd == self.OUTGOING_UPDATE):
                        #logging.debug("Node: " + str(self.rank) + " Adding outgoing update:" + str(msg))
                        if (len(self.outgoingUpdates) >= self.outgoingUpdatesBufferSize):
                            self.sendUpdate(self.outgoingUpdates[0])
                            self.outgoingUpdates.pop(0)
                        self.outgoingUpdates.append(msg)

                    elif (cmd == self.BARRIER_START):
                        self.barrierStart()

                    elif (cmd == self.SHUTDOWN):
                        #logging.debug("Node: " + str(self.rank) + " Shutting down")
                        self.running = False

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

                    else:
                        time.sleep(0.000001)

            except Exception as e:
                logging.exception(e)
                logging.critical("CommThread exception")
