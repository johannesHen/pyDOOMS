import random
import math
import time
import sys, os
from numpy import linalg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import PyDOOMS
from random import *

myname = eval(sys.argv[1])
numberOfClients = eval(sys.argv[2])

blocksize = 3

def printMatrix(A):
	print "Matrix:"
	for i in range(len(matrix)):
			print matrix[i]
	 	
def generateMatrix(size):
	random_matrix = [[float(randrange(1,10)) for e in range(size)] for e in range(size)]
	return random_matrix
 
matrixSize = 4
L = [[0.0 for i in range(matrixSize)] for j in range(matrixSize)]
U = [[0.0 for i in range(matrixSize)] for j in range(matrixSize)]
A = generateMatrix(4)


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
    return (L, U, P)

def invertMatrix(m):
	return linalg.inv(m)

def multiplyMatrix(A, B):
    TB = zip(*B)
    return [[sum(ea*eb for ea,eb in zip(a,b)) for b in TB] for a in A]

def factorizeDiagonal(A):
	size = len(A)
	diagBlock = []
	#for i in range(0, size, blocksize):	
	for i in range(0,blocksize):
		X = []
		for j in range(0,blocksize):
		 	X.append(A[i][j])
		diagBlock.append(X)	
	print diagBlock

def decompose(A, blocksize):
	if len(A) % blocksize != 0:
		print "error"
		return "error"

	size = len(A)	
	L = [[0.0 for i in range(size)] for j in range(size)]
	U = [[0.0 for i in range(size)] for j in range(size)]

	
print "Matrix to factorize", A
factorizeDiagonal(A)
		

PyDOOMS.shutdown()

