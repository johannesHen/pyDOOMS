import logging

class ObjectStore(object):
    """
    Class containing a dictionary of all shared objects and methods to manipulate it.
    Objects are indexed by their IDs.
    """

    def __init__(self):
        self.objects = dict()

    def addObject(self, object):
        """
        Adds the object to the object store dictionary
        """
        #logging.debug("object" + str(object.ID) + " added to dict")
        self.objects[object.ID] = object

    def setDictionary(self, dict):
        """
        Used for multiprocessing purposes
        """
        #logging.debug("dict changed")
        self.objects = dict