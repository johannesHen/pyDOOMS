from PyDOOMS import SharedObject

class RowChunk(SharedObject):
    """
    SharedObject representing part of a row in a matrix
    """

    def __init__(self, ID, rowChunk):
        self.rowChunk = rowChunk
        SharedObject.__init__(self, ID)
