
class ObjectStore(object):
    """
    Class containing a dictionary of all shared objects and methods to manipulate it.
    Objects are indexed by their IDs.
    """

    objects = dict()

    def addObject(self, object):
        """
        Adds the object to the object store dictionary
        """
        self.objects[object.ID] = object