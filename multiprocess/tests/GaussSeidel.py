"""
Gauss-Seidel implementation using PyDOOMS to share matrix rows and worker information
"""

import sys, os, time, logging
from random import *
import pickle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MatrixRow import MatrixRow
from WorkerInfo import WorkerInfo
import PyDOOMS

def worker(workerID, matrixSize, tolerance):
    numberOfWorkers = PyDOOMS.getNumOfWorkers()

    matrixRowOffset = 100

    if workerID == 0:
        for r in range(matrixRowOffset, matrixRowOffset + matrixSize):
            mr = MatrixRow(r, generateMatrixRow(matrixSize))

        for w in range(numberOfWorkers):
            WorkerInfo(w)

    PyDOOMS.barrier()

    chunkSize = matrixSize / numberOfWorkers
    lbound = max(workerID * chunkSize, 1)
    rbound = min((workerID + 1) * chunkSize, matrixSize - 1)

    logging.debug("Worker: "  + str(workerID) + " assigned columns " + str(range(lbound,rbound)))

    start = time.time()
    for iteration in range(1): # while globalError <= tolerance:

        PyDOOMS.get(workerID).error = 0.0

        for row in range(1,matrixSize-1):


            if (workerID != 0):
                while (PyDOOMS.get(workerID - 1).progress < row):
                    logging.debug("Worker: " + str(workerID) + " Waiting for previous worker")
                    PyDOOMS.barrier()
                    logging.debug("Worker: " + str(workerID) + " Done waiting")

            logging.debug("Worker: "  + str(workerID) + " Starting with row: " + str(row))

            workerInfo = PyDOOMS.get(workerID)
            previousMatrixRow = PyDOOMS.get(matrixRowOffset + row - 1)
            currentMatrixRow = PyDOOMS.get(matrixRowOffset + row)
            nextMatrixRow = PyDOOMS.get(matrixRowOffset + row + 1)

            for column in range(lbound, rbound):
                newValue = 0.25 * (nextMatrixRow.row[column] + previousMatrixRow.row[column] +
                                   currentMatrixRow.row[column+1] + currentMatrixRow.row[column-1])

                #logging.debug("Worker:",workerID,"Element",row,",",column,"calculated to",newValue

                #logging.debug("local error:",abs(currentMatrixRow.row[column] - newValue)
                workerInfo.error += abs(currentMatrixRow.row[column] - newValue)

                currentMatrixRow.row[column] = newValue

            workerInfo.progress = row
            PyDOOMS._comm.addOutgoingUpdate(workerInfo.ID, "progress", workerInfo.progress)
            PyDOOMS._comm.addOutgoingUpdate(workerInfo.ID, "error", workerInfo.error)
            PyDOOMS._comm.addOutgoingUpdate(matrixRowOffset + row, "row", currentMatrixRow.row)
            logging.debug("Worker: " + str(workerID) + " Done with row: " + str(row))
            PyDOOMS.barrier()


        if (workerID != 0):
            previousWorker = PyDOOMS.get(workerID - 1)
            previousWorker.progress = 0
            PyDOOMS._comm.addOutgoingUpdate(previousWorker.ID, "progress", previousWorker.progress)

        if (workerID == numberOfWorkers - 1):
            globalError = 0.0

            for w in range(numberOfWorkers):
                globalError += PyDOOMS.get(w).error

            logging.debug("GlobalError: " + str(globalError))

        for i in range(workerID,numberOfWorkers):
            PyDOOMS.barrier()

    logging.debug("Worker: " + str(workerID) + " done in " + str(time.time() - start) + " seconds")



def generateMatrix(size):
    random_matrix = [[float(randrange(0,5)) for e in range(size)] for e in range(size)]
    return random_matrix

def generateMatrixRow(length):
    random_row = [float(randrange(0,5)) for e in range(length)]
    return random_row

def printMatrix(matrix):
    for i in range(len(matrix)):
        logging.debug(str(matrix[i]))


matrixSize = 446

PyDOOMS.execute(worker, matrixSize, 1)