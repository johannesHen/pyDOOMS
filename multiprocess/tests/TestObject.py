import PyDOOMS

class TestObject(PyDOOMS.SharedObject):
    '''
    Object used for testing, a subclass of PyDOOMS.SharedObject with an additional attribute value
    '''
    def __init__(self, ID):
        self.value = 0
        PyDOOMS.SharedObject.__init__(self, ID)