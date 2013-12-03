"""
Red-Black Gauss-Seidel implementation using PyDOOMS to share matrix rows and worker information
"""

import sys, os, time, logging
from random import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkerInfo import WorkerInfo
from MatrixRow import MatrixRow
import PyDOOMS

def worker(workerID, matrixSize, tolerance):
    global numberOfWorkers, matrixOffset
    numberOfWorkers = PyDOOMS.getNumberOfWorkers()
    matrixOffset = 100

    chunkSize = (matrixSize-2) / numberOfWorkers

    if workerID == 0:
        if ((matrixSize - 2) % numberOfWorkers) != 0:
            print "Warning: Matrix size incompatible with number of workers, not all columns will be calculated"

        generateSharedMatrixRows(matrixSize)
        #printMatrixRows(matrixSize)

        for w in range(numberOfWorkers):
            WorkerInfo(w)


    PyDOOMS.barrier()

    logging.debug("Worker: " + str(workerID) + " assigned rows " + str(workerID*chunkSize+1) + "-" + str(workerID*chunkSize + chunkSize + 1))


    start = time.time()
    for iteration in range(1): # or while globalError <= tolerance:

        workerInfo = PyDOOMS.get(workerID)
        workerInfo.error = 0.0

        enum = dict(enumerate(['Red', 'Black']))
        for color in enum:

            for row in range(workerID*chunkSize + 1,workerID*chunkSize + chunkSize + 1):

                #logging.debug("Worker: "  + str(workerID) + " Starting with row: " + str(row))

                northRow = PyDOOMS.get(matrixOffset + row - 1)
                centerRow = PyDOOMS.get(matrixOffset + row)
                southRow = PyDOOMS.get(matrixOffset + row + 1)

                for column in range((color + row) % 2 + 1, matrixSize-1, 2):
                    newValue = 0.25 * (northRow.row[column] + southRow.row[column] +
                                       centerRow.row[column-1] + centerRow.row[column+1])

                    #logging.debug("Worker:" + str(workerID) + str(" Element ") + str(row) + "," + str(column) + " calculated to " + str(newValue))
                    #logging.debug("local error:" + str(abs(centerRow.row[column] - newValue)))
                    workerInfo.error += abs(centerRow.row[column] - newValue)

                    centerRow.row[column] = newValue

                PyDOOMS.objectUpdated(centerRow, "row")

            PyDOOMS.objectUpdated(workerInfo, "error")

            #logging.debug("Worker: " + str(workerID) + " Barrier")
            PyDOOMS.barrier()

        if (workerID == numberOfWorkers - 1):
            globalError = 0.0

            for w in range(numberOfWorkers):
                globalError += PyDOOMS.get(w).error

            logging.debug("GlobalError: " + str(globalError))


    logging.debug("Worker: " + str(workerID) + " done in " + str(time.time() - start) + " seconds")



def generateSharedMatrixRows(matrixSize):
    for row in range(matrixOffset,matrixOffset + matrixSize):
        MatrixRow(row, [float(randrange(0,10)) for e in range(matrixSize)])


def printMatrixRows(matrixSize):
    for row in range(matrixSize):
        logging.debug(str(PyDOOMS.get(matrixOffset + row).row))


matrixSize = 1002

PyDOOMS.execute(worker, matrixSize, 1)