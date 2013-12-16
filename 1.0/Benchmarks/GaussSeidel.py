"""
Gauss-Seidel implementation using PyDOOMS to share chunks of matrix rows and worker information
"""

import sys, os, time, logging
from random import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RowChunk import RowChunk
from WorkerInfo import WorkerInfo
import PyDOOMS


def gaussSeidel(workerID, matrixSize):
    global numberOfWorkers, matrixOffset
    numberOfWorkers = PyDOOMS.getNumberOfWorkers()
    matrixOffset = 100

    chunkSize = (matrixSize-2) / numberOfWorkers

    if workerID == 0:
        if ((matrixSize - 2) % numberOfWorkers) != 0:
            print "Warning: Matrix size incompatible with number of workers, some columns may not be calculated"

        matrix = generateMatrix(matrixSize)

        generateSharedRowChunks(matrix, chunkSize)

        for w in range(numberOfWorkers):
            WorkerInfo(w)

    PyDOOMS.barrier()

    logging.info("Worker: "  + str(workerID) + " assigned chunk " + str(workerID+1))

    start = time.time()
    for iteration in range(1):

        workerInfo = PyDOOMS.get(workerID)
        workerInfo.error = 0.0

        for row in range(1,matrixSize-1):
            if (workerID != 0):
                while (PyDOOMS.get(workerID - 1).progress < row):
                    PyDOOMS.barrier()

            workerChunk = workerID + 1

            westChunk = PyDOOMS.get(getChunkRowIndex(row,workerChunk-1))
            northChunk = PyDOOMS.get(getChunkRowIndex(row-1,workerChunk))
            eastChunk = PyDOOMS.get(getChunkRowIndex(row,workerChunk+1))
            southChunk = PyDOOMS.get(getChunkRowIndex(row+1,workerChunk))
            centerChunk = PyDOOMS.get(getChunkRowIndex(row,workerChunk))

            if chunkSize == 1:
                for column in range(len(centerChunk.rowChunk)):
                    newValue = 0.25 * (northChunk.rowChunk[column] + southChunk.rowChunk[column] +
                                       eastChunk.rowChunk[column] + westChunk.rowChunk[column])

                    workerInfo.error += abs(centerChunk.rowChunk[column] - newValue)
                    centerChunk.rowChunk[column] = newValue

            else:
                for column in range(len(centerChunk.rowChunk)):
                    if column == 0:
                        newValue = 0.25 * (northChunk.rowChunk[column] + southChunk.rowChunk[column] +
                                           westChunk.rowChunk[chunkSize-1] + centerChunk.rowChunk[column+1])

                    elif column == chunkSize-1:
                        newValue = 0.25 * (northChunk.rowChunk[column] + southChunk.rowChunk[column] +
                                           centerChunk.rowChunk[column-1] + eastChunk.rowChunk[0])

                    else:
                        newValue = 0.25 * (northChunk.rowChunk[column] + southChunk.rowChunk[column] +
                                           centerChunk.rowChunk[column-1] + centerChunk.rowChunk[column+1])

                    workerInfo.error += abs(centerChunk.rowChunk[column] - newValue)
                    centerChunk.rowChunk[column] = newValue

            workerInfo.progress = row
            PyDOOMS.objectUpdated(workerInfo, "progress")
            PyDOOMS.objectUpdated(workerInfo, "error")
            PyDOOMS.objectUpdated(centerChunk, "rowChunk")
            PyDOOMS.barrier()


        if (workerID != 0):
            previousWorker = PyDOOMS.get(workerID - 1)
            previousWorker.progress = 0
            #PyDOOMS._comm.addOutgoingUpdate(previousWorker.ID, "progress", previousWorker.progress)

        if (workerID == numberOfWorkers - 1):
            globalError = 0.0

            for w in range(numberOfWorkers):
                globalError += PyDOOMS.get(w).error

            logging.info("GlobalError: " + str(globalError))

        for i in range(workerID,numberOfWorkers):
            PyDOOMS.barrier()

    logging.info("Worker: " + str(workerID) + " done in " + str(time.time() - start) + " seconds")



def getChunkRowIndex(row,chunk):
    return matrixOffset + row * matrixSize + chunk


def generateSharedRowChunks(matrix, chunkSize):
    for row in range(matrixSize):
        # First column has single element chunks
        firstColumn = matrix[row][0:1]

        # Pad to use it as any other chunk
        leftmostChunk = []
        for e in range(chunkSize-1):
            leftmostChunk.append(None)
        leftmostChunk.append(firstColumn[0])

        RowChunk(getChunkRowIndex(row,0), leftmostChunk)

        # Create regular chunks
        for i in range(0,numberOfWorkers):
            RowChunk(getChunkRowIndex(row,i+1), matrix[row][i*chunkSize + 1:i*chunkSize+chunkSize+1])

        # Last column has single element chunks
        lastColumn = matrix[row][matrixSize-1:matrixSize]

        # Pad to use it as any other chunk
        rightmostChunk = []
        rightmostChunk.append(lastColumn[0])
        for e in range(chunkSize-1):
            rightmostChunk.append(None)

        RowChunk(getChunkRowIndex(row,numberOfWorkers+1),rightmostChunk)


def generateMatrix(size):
    random_matrix = [[float(randrange(0,10)) for e in range(size)] for e in range(size)]
    return random_matrix


def printMatrix(matrix):
    for i in range(len(matrix)):
        print(str(matrix[i]))



matrixSize = 1200

PyDOOMS.execute(gaussSeidel, matrixSize)