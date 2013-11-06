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

    outgoingUpdatesBufferSize = 10


    def __init__(self, comm, sQueue, rQueue):
        threading.Thread.__init__(self)
        self.outgoingUpdates = []
        self.incomingUpdates = []
        self.communication = comm
        self.sendQueue = sQueue
        self.receiveQueue = rQueue
        self.barrierUp = False
        self.barrierAcks = self.size - 1
        self.running = True


    def broadcast(self, msg, tag):
        """
        Sends message msg with tag tag to all nodes in the MPI.COMM_WORLD communicator
        except the local node
        """
        for i in [x for x in range(self.size) if x != self.rank]:
            #logging.debug("Rank " + str(self.rank) + " broadcast to " + str(i))
            self.comm.send(msg, i, tag)


    def receiveObject(self, obj):
        """
        Adds the object obj to the object store in the local node
        """
        self.communication.objStore.addObject(obj)


    def sendUpdates(self):
        """
        Broadcasts all updates in self.outgoingUpdates and then clears self.outgoingUpdates
        """
        #logging.debug("OutgoingUpdates: " + str(self.outgoingUpdates))
        for update in self.outgoingUpdates:
            self.sendUpdate(update)
        self.outgoingUpdates = []


    def sendUpdate(self, update):
        """
        Broadcast message update
        """
        #logging.debug("Process "+str(self.comm.rank) + " Sending update " + str(update))
        self.broadcast(update, self.SEND_UPDATE)


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
        If in a barrier, this method updates the attribute attr to the new value value in the object with id id
        Otherwise, the update is appended to the list of incoming updates to be handled later
        """
        if (self.barrierUp):
            self.communication.objStore.objects[id].update(attr,value)
        else:
            self.incomingUpdates.append((id, attr, value))
            if (id,attr,value) in self.outgoingUpdates:
                logging.debug("Process: " + str(self.rank) + " incoming and outgoing update for same message in cmd=OUTGOINGUPDATE")


    def processUpdates(self):
        """
        Applies all updates in self.incomingUpdates to the corresponding objects
        """
        for upd in self.incomingUpdates:
            self.communication.objStore.objects[upd[0]].update(upd[1], upd[2])


    def barrierStart(self):
        """
        Initialize barrier synchronization by merging and sending outgoing updates,
        broadcasting that all updates has been sent, and finally process previously
        received updates
        """
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

        """
        If the thread has already received barrier done messages from all other nodes
        it wont receive any more and the check for completion must be done here
        """
        if (self.barrierAcks == self.size - 1):
            self.barrierUp = False
            self.comm.barrier()
            self.receiveQueue._put(self.BARRIER_DONE)


    def barrierAck(self):
        """
        Increment the number of barrierAcks and if all remote nodes has sent a BARRIER_DONE message,
        mpi4py's barrier function is called and later a BARRIER_DONE message is sent to the main thread,
        to indicate that the barrier synchronization is done
        """
        self.barrierAcks += 1
        if (self.barrierAcks == self.size - 1):
            self.barrierUp = False
            self.comm.barrier()
            self.receiveQueue._put(self.BARRIER_DONE)


    def run(self):
        """
        Method containing the thread's run loop used to send or otherwise handle messages received
        from the sendQueue and to receive and handle messages from remote nodes.
        Commands or messages from the sendQueue has top priority for handling, receives are handled
        when the sendQueue is empty, and when no message are sent or received the thread sleeps
        """

        #logging.debug("Process " + str(self.rank) + " - New CommThread starting")
        while (self.running):
            try:
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
                        if (len(self.outgoingUpdates) >= self.outgoingUpdatesBufferSize):
                            self.sendUpdate(self.outgoingUpdates[0])
                            self.outgoingUpdates.pop(0)
                        self.outgoingUpdates.append(msg)
                        if msg in self.incomingUpdates:
                            logging.debug("Process: " + str(self.rank) + " incoming and outgoing update for same message in cmd=OUTGOINGUPDATE")

                    elif (cmd == self.SHUTDOWN):
                        #logging.debug("Shutting down")
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
                        time.sleep(0.0000001)

            except Exception as e:
                logging.exception(e)
                logging.critical("CommThread exception")