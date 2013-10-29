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


    def __setattr__(self, attr, value):
        #if ((attr in self.getSubclassAttr()) or (attr not in self.getAllAttr())): # Move?!?!

        self.__dict__[attr] = value
        #manager.comm.addOutgoingUpdate(self.ID, attr, value)
        #else:
        #    self.__dict__[attr] = value

    '''def getSubclassAttr(self):
        return set(dir(self))-set(dir(SharedObject))

    def getAllAttr(self):
        return set(dir(self)) | set(dir(SharedObject))'''


def get(i):
    obj = getObject(i)
    if (obj is not None):
        return obj
    else:
        raise Exception('Object not found')