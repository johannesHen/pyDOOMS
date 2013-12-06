# matrices.py
# Partly written in class on Thu 6-Oct with many additions in an
# optional lecture on Sat 8-Oct, and then one more addition (changing
# floats to fractions) by motivated students after the lecture.  :-)
# As usual, with code written in real-time in class, this may have
# some stylistic shortcomings (such as lacking comments) and may
# even have a bug lurking here or there.

# This optional case study solves each of the following problems.  Each
# solution uses the solutions to the preceding problems.

# 1) Multiply two matrices
# 2) Invert a matrix
# 3) Solve a system of linear equations
# 4) Fit an exact polynomial to a list of points
# 5) Find the coefficients of the polynomial for a power sum

# This last problem needs a little explaining.  Consider this power sum:
# 1 + 2 + ... + n.  We know this equals n(n+1)/2.  We can represent this
# quadratic function by its coefficients alone, as [1/2, 1/2, 0] (ignoring
# integer division in this explanation).

# Now, the sum of the squares is: 1**2 + 2**2 + ... + n**2.  This is a cubic
# equation.  It happens to be [1/3, 1/2, 1/6, 0].  That is:
# 1**2 + ... + n**2 = (1/3)n**3 + (1/2)n**2 + (1/6)n

# In fact, for positive integer k, 1**k + ... + n**k is a (k+1)-degree
# polynomial.  The problem we are solving is to write a function which takes
# this number k, and returns the coefficients of that polynomial.

# For some test cases, you can see the expected polynomials for k=1 to k=10
# here: http://mathworld.wolfram.com/PowerSum.html

# Also, our approach for matrix multiplication needs some slight explaining.
# We basically use Gauss-Jordan Elimination to get reduced row echelon form
# while applying the same elementary row operations to an identity matrix -- in
# so doing, the identity matrix is transformed into the inverse of the original
# matrix.  Amazing!
# You can see this in action, interactively entering your own NxN matrix and
# watch the inverse matrix being derived step-by-step, here:
# http://www.math.odu.edu/~bogacki/cgi-bin/lat.cgi?c=inv

# Finally, since our solutions are all fractions, we opted to the fractions
# module in Python.  This hardly changed our original floating-point solution,
# so the code should be readable even if you are unfamiliar with the
# fractions module.

import copy
from fractions import Fraction

def copyMatrix(m):
    return copy.deepcopy(m)

def makeIdentity(n):
    result = make2dList(n,n)
    for i in xrange(n):
        result[i][i] = 1
    return result

def testMakeIdentity():
    print "Testing makeIdentity...",
    i3 = [[1,0,0],[0,1,0],[0,0,1]]
    assert(i3 == makeIdentity(3))
    print "Passed!"

def multiplyMatrices(a, b):
    # confirm dimensions
    aRows = len(a)
    aCols = len(a[0])
    bRows = len(b)
    bCols = len(b[0])
    assert(aCols == bRows) # belongs in a contract 
    rows = aRows
    cols = bCols
    # create the result matrix c = a*b
    c = make2dList(rows, cols)
    # now find each value in turn in the result matrix
    for row in xrange(rows):
        for col in xrange(cols):
            dotProduct = 0
            for i in xrange(aCols):
                dotProduct += a[row][i]*b[i][col]
            c[row][col] = dotProduct
    return c

def testMultiplyMatrices():
    print "Testing multiplyMatrices...",
    a = [ [ 1, 2, 3],
          [ 4, 5, 6 ] ]
    b = [ [ 0, 3],
          [ 1, 4],
          [ 2, 5] ]
    c = [ [ 8, 26],
          [17, 62 ] ]
    observedC = multiplyMatrices(a, b)
    assert(observedC == c)
    print "Passed!"

def multiplyRowOfSquareMatrix(m, row, k):
    n = len(m)
    rowOperator = makeIdentity(n)
    rowOperator[row][row] = k
    return multiplyMatrices(rowOperator, m)

def testMultiplyRowOfSquareMatrix():
    print "Testing multiplyRowOfSquareMatrix...",
    a = [ [ 1, 2 ],
          [ 4, 5  ] ]
    assert(multiplyRowOfSquareMatrix(a, 0, 5) == [[5, 10], [4, 5]])
    assert(multiplyRowOfSquareMatrix(a, 1, 6) == [[1, 2], [24, 30]])
    print "Passed!"

def addMultipleOfRowOfSquareMatrix(m, sourceRow, k, targetRow):
    # add k * sourceRow to targetRow of matrix m
    n = len(m)
    rowOperator = makeIdentity(n)
    rowOperator[targetRow][sourceRow] = k
    return multiplyMatrices(rowOperator, m)

def testAddMultipleOfRowOfSquareMatrix():
    print "Testing addMultipleOfRowOfSquareMatrix...",
    a = [ [ 1, 2 ],
          [ 4, 5  ] ]
    assert(addMultipleOfRowOfSquareMatrix(a, 0, 5, 1) == [[1, 2], [9, 15]])
    assert(addMultipleOfRowOfSquareMatrix(a, 1, 6, 0) == [[25, 32], [4, 5]])
    print "Passed!"

def invertMatrix(m):
    n = len(m)
    assert(len(m) == len(m[0]))
    inverse = makeIdentity(n) # this will BECOME the inverse eventually
    for col in xrange(n):
        # 1. make the diagonal contain a 1
        diagonalRow = col
        assert(m[diagonalRow][col] != 0) # @TODO: actually, we could swap rows
                                         # here, or if no other row has a 0 in
                                         # this column, then we have a singular
                                         # (non-invertible) matrix.  Let's not
                                         # worry about that for now.  :-)
        #k = Fraction(1,m[diagonalRow][col])
        k = 1.0/m[diagonalRow][col]
        m = multiplyRowOfSquareMatrix(m, diagonalRow, k)
        inverse = multiplyRowOfSquareMatrix(inverse, diagonalRow, k)
        # 2. use the 1 on the diagonal to make everything else
        #    in this column a 0
        sourceRow = diagonalRow
        for targetRow in xrange(n):
            if (sourceRow != targetRow):
                k = -m[targetRow][col]
                m = addMultipleOfRowOfSquareMatrix(m, sourceRow, k, targetRow)
                inverse = addMultipleOfRowOfSquareMatrix(inverse, sourceRow,
                                                         k, targetRow)
    # that's it!
    return inverse

def testInvertMatrix():
    print "Testing invertMatrix...",
    a = [ [ 1, 2 ], [ 4, 5  ] ]
    aInverse = invertMatrix(a)
    identity = makeIdentity(len(a))
    assert (almostEqualMatrices(identity, multiplyMatrices(a, aInverse)))
    a = [ [ 1, 2, 3], [ 2, 5, 7 ], [3, 4, 8 ] ]
    aInverse = invertMatrix(a)
    identity = makeIdentity(len(a))
    assert (almostEqualMatrices(identity, multiplyMatrices(a, aInverse)))
    print "Passed!"

def solveSystemOfEquations(A, b):
    return multiplyMatrices(invertMatrix(A), b)

def testSolveSystemOfEquations():
    print "Testing solveSystemOfEquations...",
    # 3x + 2y - 2z = 10
    # 2x - 4y + 8z =  0
    # 4x + 4y - 7z = 13
    # x = 2, y = 3, z = 1
    A = [ [3,  2, -2],
          [2, -4,  8],
          [4,  4, -7] ]
    b = [ [ 10 ],
          [  0 ],
          [ 13 ] ]
    observedX = solveSystemOfEquations(A,b)
    expectedX = [ [ 2 ],
                  [ 3 ],
                  [ 1 ] ]
    assert(almostEqualMatrices(observedX, expectedX))
    print "Passed!"

def fitExactPolynomial(pointList):
    n = len(pointList)
    degree = n - 1
    # 1. make A
    A = make2dList(n,n)
    for row in xrange(n):
        for col in xrange(n):
            x = pointList[row][0]
            exponent = degree - col
            A[row][col] = x**exponent
    # 2. make b
    b = make2dList(n,1)
    for row in xrange(n):
        y = pointList[row][1]
        b[row][0] = y
    # use system solver to find solution
    return solveSystemOfEquations(A, b)

def testFitExactPolynomial():
    print "Testing fitPolynomialExactly...",
    def f(x): return 3*x**3 + 2*x**2 + 4*x + 1
    expected = [[3], [2], [4], [1]]
    pointList = [(1,f(1)), (2,f(2)), (5,f(5)), (-3,f(-3))]
    observed = fitExactPolynomial(pointList)
    assert(almostEqualMatrices(observed, expected))    
    print "Passed!"

def findCoefficientsOfPowerSum(k):
    # Assume f(n) = 1**k + ... + n**k
    # We argued by handwaving-ish-calculusy-stuff that f(n) is
    # a polynomial of degree (k+1)
    # We need (k+2) points to fit just such a polynomial
    pointList = []
    y = 0    
    for n in xrange(1,k+3):
		x = Fraction(n, 1)
        # y = 1**k + ... + n**k
		y += x**k
		pointList += [(x,y)]
    return fitExactPolynomial(pointList)

def testFindCoefficientsOfPowerSum():
    print "Testing findCoefficientsOfPowerSum..."
    # Not a formal test here, just printing the answers.
    # Check here for expected values:
    # http://mathworld.wolfram.com/PowerSum.html
    for k in xrange(10):
        print "k = %d:" % k,
        printMatrix(findCoefficientsOfPowerSum(k))
    print "Passed!"

def almostEqualMatrices(m1, m2):
    # verifies each element in the two matrices are almostEqual to each other
    # (and that the two matrices have the same dimensions).
    if (len(m1) != len(m2)): return False
    if (len(m1[0]) != len(m2[0])): return False
    for row in xrange(len(m1)):
        for col in xrange(len(m1[0])):
            if not almostEqual(m1[row][col], m2[row][col]):
                return False
    return True

def almostEqual(d1, d2):
    epsilon = 0.00001
    return abs(d1 - d2) < epsilon

def make2dList(rows, cols):
    a=[]
    for row in xrange(rows): a += [[0]*cols]
    return a
    
def printMatrix(a):
    def valueStr(value):
        if (isinstance(value, Fraction)):
            (num, den) = (value.numerator, value.denominator)
            if ((num == 0) or (den == 1)): return str(num)
            else: return str(num) + "/" + str(den)
        else:
            return str(value)
    def maxItemLength(a):
        maxLen = 0
        rows = len(a)
        cols = len(a[0])
        for row in xrange(rows):
            for col in xrange(cols):
                maxLen = max(maxLen, len(valueStr(a[row][col])))
        return maxLen
    if (a == []):
        # So we don't crash accessing a[0]
        print []
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print "[",
    for row in xrange(rows):
        if (row > 0) and (len(a[row-1]) > 1): print "\n  ",
        print "[",
        for col in xrange(cols):
            if (col > 0): print ",",
            # The next 2 lines print a[row][col] with the given fieldWidth
            format = "%" + str(fieldWidth) + "s"
            print format % valueStr(a[row][col]),
        print "]",
    print "]"
