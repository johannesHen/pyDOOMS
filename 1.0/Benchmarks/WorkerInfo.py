from PyDOOMS import SharedObject

class WorkerInfo(SharedObject):
    """
    SharedObject containing information about workers in the Gauss-Seidel implementation
    """

    def __init__(self, ID):
        self.ID = ID
        self.error = 0.0
        self.progress = 0

        SharedObject.__init__(self, ID)