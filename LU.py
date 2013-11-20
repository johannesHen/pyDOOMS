
from numpy import linalg
from pprint import pprint
 

def invertMatrix(matrix):
    print linalg.inv(matrix);

def matrixMul(A, B):
    TB = zip(*B)
    return [[sum(ea*eb for ea,eb in zip(a,b)) for b in TB] for a in A]
 
def pivotize(m):
    """Creates the pivoting matrix for m."""
    n = len(m)
    ID = [[float(i == j) for i in xrange(n)] for j in xrange(n)]
    for j in xrange(n):
        row = max(xrange(j, n), key=lambda i: m[i][j])
        if j != row:
            ID[j], ID[row] = ID[row], ID[j]
    return ID
 
def lu(A):
    """Decomposes a nxn matrix A by PA=LU and returns L, U and P."""
    n = len(A)
    L = [[0.0] * n for i in xrange(n)]
    U = [[0.0] * n for i in xrange(n)]
    #P = pivotize(A)
    #A2 = matrixMul(P, A)
    for j in xrange(n):
        L[j][j] = 1.0
        for i in xrange(j+1):
            s1 = sum(U[k][j] * L[i][k] for k in xrange(i))
            U[i][j] = A[i][j] - s1
        for i in xrange(j, n):
            s2 = sum(U[k][j] * L[i][k] for k in xrange(j))
            L[i][j] = (A[i][j] - s2) / U[j][j]
    return (L, U)


def ludec(A):
    L = [[0.0 for i in range(len(A))] for j in range(len(A))]
    U = [[0.0 for i in range(len(A))] for j in range(len(A))]
    try:
        for i in range(0, len(A)):
            L[i][0] = A[i][0]           #   L:deside 1 column.
            U[0][i] = A[0][i]/A[0][0]   #   U:deside 1 row.
        for k in range(1, len(A)):
            for i in range(0, k):
                L[i][k] = U[k][i] = 0.0 #   initialize the element to be updated.
            for i in range(k, len(A)):
                L[i][k] = A[i][k]
                for m in range(0, k):
                    L[i][k] -= L[i][m] * U[m][k]
            U[k][k] = 1.0               #   U:diagonal element is 1
            for i in range(k + 1, len(A)):
                U[k][i] = A[k][i]
                for m in range(0, k):
                    U[k][i] -= L[k][m] * U[m][i]
                U[k][i] /= L[k][k]
    except ZeroDivisionError:
        print "This matrix can't do LU Decomposition."
    return (L, U)

def decompose(A, blocksize):
    if len(A) % blocksize != 0:
        print "error"
        return "error"

    L = [[0 for x in range(size)] for x in range(size)]
    U = [[0 for x in range(size)] for x in range(size)]

x = [[3.0, 4.0], [4.0, 1.0]]     


L,U=lu(x)

print "L: ", L
print "U: ", U
 
LU = matrixMul(L,U)
print LU

