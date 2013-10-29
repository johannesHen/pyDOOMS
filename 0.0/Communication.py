import time
import logging
import Queue
import CommThread

class Communication:

    def __init__(self, man):
        self.manager = man
        self.sendQueue = Queue.Queue()
        self.receiveQueue = Queue.Queue()
        self.commThread = CommThread.CommThread(self, self.sendQueue, self.receiveQueue)
        self.commThread.daemon = True
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