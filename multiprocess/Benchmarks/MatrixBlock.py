from PyDOOMS import SharedObject

class MatrixBlock(SharedObject):
    """
    Class representing a matrix block
    """

    def __init__(self, ID, r, c, b):
        self.r = r
        self.c = c
        self.block = b
        SharedObject.__init__(self, ID)
