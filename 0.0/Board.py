from PyDOOMS import SharedObject

class Board(SharedObject):
    """
    Class representing a board in the monte-carlo algorithm
    """

    def __init__(self, ID):
        SharedObject.__init__(self, ID)
        self.hits = 0
        self.darts = 0
        self.ready = False

    def hit(self):
        self.hits = self.hits + 1
        self.darts = self.darts + 1

    def miss(self):
        self.darts = self.darts + 1

    def calc_pi(self):
        return (4.0 * self.hits) / self.darts