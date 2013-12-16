"""
LU factorization implementation using PyDOOMS to share matrix blocks
"""

import time, logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from random import *
from matrices import *
from MatrixBlock import MatrixBlock
import PyDOOMS


size = 100
blockSize = 10
blocksPerSide = size/blockSize

matrixOffset = 0
LOffset = blocksPerSide*blocksPerSide
UOffset = blocksPerSide*blocksPerSide*2


def printMatrix(matrix):
    for i in range(len(matrix)):
            print matrix[i]


def multiplyMatrix(A, B):
    TB = zip(*B)
    return [[sum(ea*eb for ea,eb in zip(a,b)) for b in TB] for a in A]


def generateSharedMatrixBlocks(size):
    for i in range(blocksPerSide):
        for j in range(blocksPerSide):
            # Create input matrix
            generateSharedBlock(matrixOffset + (i * blocksPerSide+j), i*blockSize, j*blockSize, blockSize)

            # Create empty L matrix
            generateSharedZeroBlock(LOffset + (i * blocksPerSide+j), i*blockSize, j*blockSize, blockSize)

            # Create empty U matrix
            generateSharedZeroBlock(UOffset + (i * blocksPerSide+j), i*blockSize, j*blockSize, blockSize)


def generateSharedBlock(id, x, y, size):
    random_block = [[float(randrange(1,10)) for e in range(size)] for e in range(size)]
    MatrixBlock(id, x, y, multiplyMatrix(random_block, random_block))


def generateSharedZeroBlock(id, x, y, size):
    zero_block = [[0.0 for e in range(size)] for e in range(size)]
    MatrixBlock(id, x, y, zero_block)


def betterLU(A):
    L = [[0.0 for i in range(len(A))] for j in range(len(A))]
    U = [[0.0 for i in range(len(A))] for j in range(len(A))]
    try:
        for i in range(0, len(A)):
            L[i][0] = A[i][0]            # L:deside 1 column.
            U[0][i] = A[0][i]/A[0][0]    # U:deside 1 row.
        for k in range(1, len(A)):
            for i in range(0, k):
                L[i][k] = U[k][i] = 0.0    #    initialize the element to be updated.
            for i in range(k, len(A)):
                L[i][k] = A[i][k]
                for m in range(0, k):
                    L[i][k] -= L[i][m] * U[m][k]
            U[k][k] = 1.0                #    U:diagonal element is 1
            for i in range(k + 1, len(A)):
                U[k][i] = A[k][i]
                for m in range(0, k):
                    U[k][i] -= L[k][m] * U[m][i]
                U[k][i] /= L[k][k]
    except ZeroDivisionError:
        print "This matrix can't do LU Decomposition."
    return L, U


def subtractMatrix(a,b):
    return [map(float.__sub__, i, j) for i,j in zip(a,b)]


def multiplyLU():
    L = [[0.0 for i in range(size)] for j in range(size)]
    U = [[0.0 for i in range(size)] for j in range(size)]

    for id in range(LOffset, LOffset + blocksPerSide*blocksPerSide):
        m = PyDOOMS.get(id)
        #print "adding block",id,"with x,y",m.r,m.c
        for r in range(len(m.block)):
            for c in range(len(m.block)):
                L[m.r + r][m.c + c] = m.block[r][c]

    for id in range(UOffset, UOffset + blocksPerSide*blocksPerSide):
        m = PyDOOMS.get(id)
        #print "adding block",id,"with x,y",m.r,m.c
        for r in range(len(m.block)):
            for c in range(len(m.block)):
                U[m.r + r][m.c + c] = m.block[r][c]

    #print "L:"
    #printMatrix(L)
    #print "U:"
    #printMatrix(U)
    R = multiplyMatrix(L,U)
    print "R:"
    printMatrix(R)


def printBlockMatrix(startingID):
    M = [[0.0 for i in range(size)] for j in range(size)]

    for id in range(startingID, startingID + blocksPerSide*blocksPerSide):
        m = PyDOOMS.get(id)
        #print "adding block",id,"with x,y",m.r,m.c
        for r in range(len(m.block)):
            for c in range(len(m.block)):
                M[m.r + r][m.c + c] = m.block[r][c]

    printMatrix(M)


def workerList(size):
    list = []
    for i in range(blocksPerSide+1):
        for j in range(i*i):
            list.append(j % PyDOOMS.getNumberOfWorkers())
    return list


def getMatrixBlock(offset, i,j):
    return PyDOOMS.get(offset + i * blocksPerSide + j)


# Worker function
def LUdecomp(workerID):
    if workerID==0:
        setupStart = time.time()

        generateSharedMatrixBlocks(size)

        print "Setup done in ", time.time() - setupStart, "seconds."
        #print "Matrix:"
        #printBlockMatrix(matrixOffset)

    start = time.time()


    for x in range(blocksPerSide):

        if workerID == workerList.pop():
            logging.debug("Worker" +str(workerID) + "working on diagonal " + str(x) + str(",") + str(x))
            A = getMatrixBlock(matrixOffset, x, x)
            L = getMatrixBlock(LOffset, x, x)
            U = getMatrixBlock(UOffset, x, x)

            l,u = betterLU(A.block)
            L.block = l
            U.block = u

            PyDOOMS.objectUpdated(L, "block")
            PyDOOMS.objectUpdated(U, "block")

        PyDOOMS.barrier()

        for i in range(x+1,blocksPerSide):
            if workerID == workerList.pop():
                logging.debug("Worker" +str(workerID) + "working on U " + str(x) + str(",") + str(i))
                A = getMatrixBlock(matrixOffset, x, i)
                L = getMatrixBlock(LOffset, x, x)
                U = getMatrixBlock(UOffset, x, i)

                U.block = multiplyMatrix(invertMatrix(L.block), A.block)
                PyDOOMS.objectUpdated(U, "block")

        for j in range(x+1,blocksPerSide):
            if workerID == workerList.pop():
                logging.debug("Worker" +str(workerID) + "working on L " + str(j) + str(",") + str(x))
                A = getMatrixBlock(matrixOffset, j, x)
                L = getMatrixBlock(LOffset, j, x)
                U = getMatrixBlock(UOffset, x, x)

                L.block = multiplyMatrix(A.block, invertMatrix(U.block))
                PyDOOMS.objectUpdated(L, "block")

        PyDOOMS.barrier()

        for j in range(x+1, blocksPerSide):
            for k in range(x+1, blocksPerSide):
                if workerID == workerList.pop():
                    logging.debug("Worker" +str(workerID) + "working on sub-block " + str(k) + str(",") + str(j))
                    A = getMatrixBlock(matrixOffset, k, j)
                    L = getMatrixBlock(LOffset, k, x)
                    U = getMatrixBlock(UOffset, x, j)

                    A.block = subtractMatrix(A.block, multiplyMatrix(L.block, U.block))
                    PyDOOMS.objectUpdated(A, "block")

        PyDOOMS.barrier()

    if workerID == 0:
        print "Done in ", time.time() - start, "seconds."
        #multiplyLU()



workerList = workerList(size)

PyDOOMS.execute(LUdecomp)
