import PyDOOMS
from TestObject2 import TestObject2

class TestObject(PyDOOMS.SharedObject):
    """
    Object used for testing, a subclass of PyDOOMS.SharedObject with an additional integer attribute value,
    and an additional object attribute objectAttr
    """

    def __init__(self, ID):
        self.value = 0
        self.objectAttr = TestObject2()
        PyDOOMS.SharedObject.__init__(self, ID)