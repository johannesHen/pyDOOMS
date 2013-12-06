import math
import time, logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from random import *
from Matrix import Matrix
from LU import LU
from matrices import *
import PyDOOMS


size = 100
blocksize = 10
blocksPerSide = size/blocksize

def printMatrix(matrix):
    for i in range(len(matrix)):
            print matrix[i]

def multiplyMatrix(A, B):
    TB = zip(*B)
    return [[sum(ea*eb for ea,eb in zip(a,b)) for b in TB] for a in A]
         
def generateMatrix(size):
    random_matrix = [[float(randrange(1,10)) for e in range(size)] for e in range(size)]
    rm = multiplyMatrix(random_matrix, random_matrix)
    return rm
 
def generateBlockMatrix(size):
    matrix = []
    for i in range(blocksPerSide):
        row = []
        for j in range(blocksPerSide):
            row.append(generateMatrix(blocksize))
        matrix.append(row)
    return matrix

def generateBlockZeroMatix(size):
    matrix = []
    for i in range(blocksPerSide):
        row = []
        for j in range(blocksPerSide):
            row.append([[0.0 for i in range(blocksize)] for j in range(blocksize)])
        matrix.append(row)
    return matrix

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


def lu(A):
    """Decomposes a nxn matrix A by A=LU and returns L and U."""
    n = len(A)
    L = [[0.0] * n for i in xrange(n)]
    U = [[0.0] * n for i in xrange(n)]
    for j in xrange(n):
        L[j][j] = 1.0
        for i in xrange(j+1):
            s1 = sum(U[k][j] * L[i][k] for k in xrange(i))
            U[i][j] = A[i][j] - s1
        for i in xrange(j, n):
            s2 = sum(U[k][j] * L[i][k] for k in xrange(j))
            L[i][j] = (A[i][j] - s2) / U[j][j]
    return L, U

def workerList(size):
    list = []
    for i in range(blocksPerSide*blocksPerSide-blocksPerSide):
        list.append(i % PyDOOMS.getNumberOfWorkers())
    return list



def LUdecomp(workerID):
    if workerID==0:
        setupStart = time.time()
        matrix = generateBlockMatrix(size)
        Matrix(0, matrix)
        l = generateBlockZeroMatix(size)
        u = generateBlockZeroMatix(size)

        for i in range(0,blocksPerSide):
            L,U = betterLU(matrix[i][i])
            #L,U = lu(matrix[i][i])
            l[i][i] = L 
            u[i][i] = U

        LU(1, l, u)
        print "Setup done in ", time.time() - setupStart, "seconds."


    start = time.time()

    PyDOOMS.barrier()

    m = PyDOOMS.get(0)
    lu2 = PyDOOMS.get(1)

    for x in range(blocksPerSide):



        for i in range(1+x,blocksPerSide):
            if workerID == workerList.pop():
                logging.debug("Worker" +str(workerID) + "is working - " + " i:" + str(i) +",x:"+ str(x))
                #logging.debug("Worker: " + str(workerID) + )
                lu2.L[i][x] = multiplyMatrix(m.matrix[i][x], invertMatrix(lu2.U[x][x]))

        for j in range(1+x, blocksPerSide):
            if workerID == workerList.pop():
                logging.debug("Worker" +str(workerID) + "is working - " + " x:" + str(x) +",j:"+ str(j))
                #logging.debug("Worker: " + str(workerID) + " x:" + str(x) +",j:"+ str(j))
                lu2.U[x][j] = multiplyMatrix(lu2.L[x][x], invertMatrix(m.matrix[x][j]))


    PyDOOMS.objectUpdated(lu2, "L")
    PyDOOMS.objectUpdated(lu2, "U")
    PyDOOMS.barrier()

    if workerID == 0:
        lumatri = PyDOOMS.get(1)
        print "Done in ", time.time() - start, "seconds."

workerList = workerList(size)

PyDOOMS.execute(LUdecomp)
