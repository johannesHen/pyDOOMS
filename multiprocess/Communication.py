import time
import logging
from multiprocessing import Queue, Pipe
import CommThread

class Communication(object):
    """
    Class used to instantiate a communication thread
    and to handle communication between workers and the communication thread.
    """

    def __init__(self, store, workers):
        """
        Start the communicating (MPI) thread and initialize one queue for messages to the CommThread
        and one pipe for each worker to receive messages from the CommThread.
        """
        self.objStore = store
        self.sendQueue = Queue()
        self.receivePipe = None
        self.workers = workers

        self.receivePipes = []
        for i in range(workers):
            self.receivePipes.append(Pipe())

        self.commThread = CommThread.CommThread(self, self.workers, self.sendQueue, self.receivePipes)
        self.commThread.start()


    def spreadObject(self, obj):
        """
        Forwards a spread-object message to the communication thread
        """
        self.sendQueue.put((self.commThread.SPREAD_OBJECT, obj))


    def addOutgoingUpdate(self, id, attr, value):
        """
        Forwards an outgoing-update message to the communication thread
        """
        self.sendQueue.put((self.commThread.OUTGOING_UPDATE, (id, attr, value)))


    def commBarrier(self):
        """
        Sends a message to the communication thread to initiate a barrier synchronization.
        Blocks until the barrier has been exited
        """
        self.sendQueue.put((self.commThread.BARRIER_START, None))

        if (self.receivePipe.recv() == self.commThread.BARRIER_DONE):
            return


    def commShutdown(self):
        """
        Sends a shutdown message to the communication thread.
        This will cause the communication thread to gracefully shut down.
        """
        #if (self.commThread.SHUTDOWN, None) not in self.sendQueue:
        self.sendQueue.put((self.commThread.SHUTDOWN, None))

    def reset(self):
        """
        Restarts the commThread and clear the object store
        """
        self.commShutdown()

        # Wait until thread is dead
        while (self.commThread.isAlive()):
            time.sleep(0.001)

        self.objStore.objects.clear()

        self.sendQueue = Queue()
        self.commThread = CommThread.CommThread(self, self.workers, self.sendQueue, self.receivePipes)
        self.commThread.start()