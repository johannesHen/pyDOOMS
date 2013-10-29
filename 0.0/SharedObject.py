from Manager import *

class SharedObject(object):
    """
    Class to be subclassed by all objects to be shared with other nodes
    """

    ID = None

    def __init__(self, id):
        self.ID = id
        registerObject(self)


    def update(self, name, value):
        self.__dict__[name] = value


def get(i):
    obj = getObject(i)
    if (obj is not None):
        return obj
    else:
        raise Exception('Object not found')