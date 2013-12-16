"""
Red-Black Gauss-Seidel implementation using PyDOOMS to share matrix rows and worker information
"""

import sys, os, time, logging
from random import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkerInfo import WorkerInfo
from MatrixRow import MatrixRow
import PyDOOMS

# Worker function
def RedBlackGaussSeidel(workerID, matrixSize):

    global numberOfWorkers, matrixOffset
    numberOfWorkers = PyDOOMS.getNumberOfWorkers()
    matrixOffset = 100

    chunkSize = (matrixSize-2) / numberOfWorkers

    if workerID == 0:
        if ((matrixSize - 2) % numberOfWorkers) != 0:
            print "Warning: Matrix size - 2 is not divisible with number of workers, some columns may not be calculated"

        start = time.time()
        generateSharedMatrixRows(matrixSize)
        logging.info("Time to generate shared matrix rows: " + str(time.time()-start))

        for w in range(numberOfWorkers):
            WorkerInfo(w)


    PyDOOMS.barrier()

    logging.info("Worker: " + str(workerID) + " assigned rows " + str(workerID*chunkSize+1) + "-" + str(workerID*chunkSize + chunkSize + 1))


    start = time.time()
    for iteration in range(1):

        workerInfo = PyDOOMS.get(workerID)
        workerInfo.error = 0.0

        enum = dict(enumerate(['Red', 'Black']))
        for color in enum:

            for row in range(workerID*chunkSize + 1,workerID*chunkSize + chunkSize + 1):

                northRow = PyDOOMS.get(matrixOffset + row - 1)
                centerRow = PyDOOMS.get(matrixOffset + row)
                southRow = PyDOOMS.get(matrixOffset + row + 1)

                for column in range((color + row) % 2 + 1, matrixSize-1, 2):
                    newValue = 0.25 * (northRow.row[column] + southRow.row[column] +
                                       centerRow.row[column-1] + centerRow.row[column+1])

                    workerInfo.error += abs(centerRow.row[column] - newValue)
                    centerRow.row[column] = newValue

                PyDOOMS.    objectUpdated(centerRow, "row")

            PyDOOMS.objectUpdated(workerInfo, "error")
            PyDOOMS.barrier()

        if (workerID == numberOfWorkers - 1):
            globalError = 0.0

            for w in range(numberOfWorkers):
                globalError += PyDOOMS.get(w).error

            logging.info("Iteration " + str(iteration+1) + " global error = " + str(globalError))

    logging.info("Worker: " + str(workerID) + " done in " + str(time.time() - start) + " seconds")



def generateSharedMatrixRows(matrixSize):
    for row in range(matrixOffset,matrixOffset + matrixSize):
        MatrixRow(row, [float(randrange(0,10)) for e in range(matrixSize)])

def printMatrixRows(matrixSize):
    for row in range(matrixSize):
        logging.debug(str(PyDOOMS.get(matrixOffset + row).row))


matrixSize = 1002

PyDOOMS.execute(RedBlackGaussSeidel, matrixSize)