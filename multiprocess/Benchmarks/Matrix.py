from PyDOOMS import SharedObject

class Matrix(SharedObject):
    """
    Class representing a matrix
    """

    def __init__(self, ID, matrix):
        self.matrix = matrix
        SharedObject.__init__(self, ID)
