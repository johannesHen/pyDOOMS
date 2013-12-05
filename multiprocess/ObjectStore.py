import logging
from multiprocessing import Manager

class ObjectStore(object):
    """
    Class containing a SyncManager dictionary of all shared objects.
    The SyncManager dictionary will be shared among all workers in a node.
    Objects are indexed by their IDs.
    """

    def __init__(self):
        self.objects = Manager().dict()

    def addObject(self, object):
        """
        Adds the object to the object store dictionary
        """
        #logging.debug("object" + str(object.ID) + " added to dict")
        self.objects[object.ID] = object