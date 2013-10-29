from Communication import *


class Manager:
    comm = None
    objects = dict()

    def __init__(self):
        self.comm = Communication(self)

    def addObject(self, object):
#        if (not object.ID in self.objects):
        self.objects[object.ID] = (object, True)


def registerObject(object):
    manager.addObject(object)
    manager.comm.spreadObject(object)

def getObject(id):
    return manager.objects[id][0]

def barrier():
    manager.comm.comm_barrier()



manager = Manager()