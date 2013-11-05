import time
import logging
import Queue
import CommThread

class Communication:
    """
    Class used to instantiate a communication thread
    and to forward outgoing message from the main thread to the communication thread using Queues
    """

    def __init__(self, store):
        """
        Initiates queues for thread communication
        and starts the communicating (MPI) thread
        """
        self.objStore = store
        self.sendQueue = Queue.Queue()
        self.receiveQueue = Queue.Queue()
        self.commThread = CommThread.CommThread(self, self.sendQueue, self.receiveQueue)
        self.commThread.start()


    def spreadObject(self, obj):
        """
        Forwards a spread-object message to the communication thread
        """
        self.sendQueue._put((self.commThread.SPREAD_OBJECT, obj))


    def addOutgoingUpdate(self, id, attr, value):
        """
        Forwards an outgoing-update message to the communication thread
        """
        self.sendQueue._put((self.commThread.OUTGOING_UPDATE, (id, attr, value)))


    def commBarrier(self):
        """
        Sends a message to the communication thread to initiate a barrier synchronization.
        Blocks until the barrier has been exited
        """
        self.sendQueue._put((self.commThread.BARRIER_START, None))

        while (True):
            try:
                if (self.receiveQueue.get(False) == self.commThread.BARRIER_DONE):
                    return
            except Queue.Empty:
                time.sleep(0.00007)


    def commShutdown(self):
        """
        Sends a shutdown message to the communication thread.
        This will cause the communication thread to gracefully shut down.
        """
        self.sendQueue._put((self.commThread.SHUTDOWN, None))

    def reset(self):
        """
        Restarts the commThread and clear the object store
        """
        self.sendQueue._put((self.commThread.SHUTDOWN, None))

        # Wait until thread is dead
        while (self.commThread.isAlive()):
            time.sleep(0.001)

        self.objStore.objects.clear()

        self.sendQueue = Queue.Queue()
        self.commThread = CommThread.CommThread(self, self.sendQueue, self.receiveQueue)
        self.commThread.start()