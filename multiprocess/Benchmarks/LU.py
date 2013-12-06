from PyDOOMS import SharedObject

class LU(SharedObject):
    """
    Class representing the L and U matrices
    """

    def __init__(self, ID, L, U):
        self.L = L
        self.U = U
        SharedObject.__init__(self, ID)