from PyDOOMS import SharedObject

class MatrixRow(SharedObject):
    """
    SharedObject representing a row in a matrix.
    """

    def __init__(self, ID, row):
        self.row = row
        SharedObject.__init__(self, ID) # In a multiprocessed environment this must be done after initializing the variables
