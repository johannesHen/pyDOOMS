import time
import logging
import Queue
import CommThread

class Communication:

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d (%(threadName)-2s) %(message)s',datefmt='%M:%S'
                    )

    def __init__(self, store):
        self.objStore = store
        self.sendQueue = Queue.Queue()
        self.receiveQueue = Queue.Queue()
        self.commThread = CommThread.CommThread(self, self.sendQueue, self.receiveQueue)
        self.commThread.start()

    def spreadObject(self, obj):
        self.sendQueue._put((self.commThread.SPREAD_OBJECT, obj))

    def addOutgoingUpdate(self, id, attr, value):
        self.sendQueue._put((self.commThread.OUTGOING_UPDATE, (id, attr, value)))

    def comm_barrier(self):
        self.sendQueue._put((self.commThread.BARRIER_START, None))

        while (True):
            try:
                if (self.receiveQueue.get(False) == self.commThread.BARRIER_DONE):
                    return
            except Queue.Empty:
                time.sleep(0.001)

    def commShutdown(self):
        #logging.debug("Sending SHUTDOWN command to thread")
        self.sendQueue._put((self.commThread.SHUTDOWN, None))