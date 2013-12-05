"""
Module containing basic tests for different aspects of the PyDOOMS library
"""

import sys, os, time
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import PyDOOMS
from TestObject import TestObject
from TestObject2 import TestObject2


def printDict():
    """
    Prints the contents of the local object store.
    """
    objects = PyDOOMS._store.objects.copy()
    logging.debug("-------------------------------------Node: " + str(PyDOOMS.getNodeID()) + " --------------------------------------------")
    for element in objects:
        if (isinstance(objects[element],TestObject)):
            logging.debug(str(element) + "  -  " + str(objects[element]))



def reset():
    """
    Reset the testing environment.
    Barriers are needed to stop workers from resetting the object store
    while other workers are running a test.
    """
    PyDOOMS.barrier()
    PyDOOMS._reset()
    PyDOOMS.barrier()


def SpreadTest1(workerID):
    """
    Tests creation and spreading of objects created in node 0
    All nodes should have all objects in their local object store at the end of the test
    """
    numOfObj = 500

    if (workerID == 0):
        for i in range(numOfObj):
            TestObject(i)

    PyDOOMS.barrier()
    # The python dictionary appears to do non-blocking inserts into the object store dict.
    # Our PyDOOMS.get() function will wait for inserts to be made, but when checking the length of the dict
    # (which should not be done outside perhaps testing) we must first wait for all inserts to complete
    time.sleep(0.02)

    if (len(PyDOOMS._store.objects) != numOfObj):
        logging.critical("Worker " + str(workerID) + " Number of objects:" + str(len(PyDOOMS._store.objects)))
        printDict()
        raise Exception



def SpreadTest2(workerID):
    """
    Tests creation and spreading of objects created in several different nodes
    All nodes should have all objects in their local object store at the end of the test
    """
    nodes = PyDOOMS.getNumberOfNodes()
    objectsPerNode = 100

    for i in range(nodes):
        if (workerID == i):
            for i in range(i*objectsPerNode,i*objectsPerNode+objectsPerNode):
                TestObject(i)

    PyDOOMS.barrier()
    # The python dictionary appears to do non-blocking inserts into the object store dict.
    # Our PyDOOMS.get() function will wait for inserts to be made, but when checking the length of the dict
    # we must first wait for all inserts to complete
    time.sleep(0.02)

    if (len(PyDOOMS._store.objects) != objectsPerNode*nodes):
        logging.critical("Worker " + str(workerID) + " Number of objects:" + str(len(PyDOOMS._store.objects)))
        printDict()
        raise Exception



def GetTest1(workerID):
    """
    Tests retrieving object references from local object store and accessing objects
    """
    numOfObj = 100

    if (workerID == 0):
        for i in range(numOfObj):
            TestObject(i)

    PyDOOMS.barrier()

    for i in range(numOfObj):
        PyDOOMS.get(i).value



def ReadLoopTest1(workerID):
    """
    Tests reading from a shared object before and after object value has been changed by another node
    """

    if (workerID == 0):
        TestObject(1)

    PyDOOMS.barrier()

    obj = PyDOOMS.get(1)
    oldValue = obj.value

    PyDOOMS.barrier()

    if (workerID == 0):
        obj.value = 1
        PyDOOMS.objectUpdated(obj, "value")

    PyDOOMS.barrier()
    obj = PyDOOMS.get(1)

    if not (oldValue == 0 and obj.value == 1):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldValue) + "," + str(obj.value) + " ")
        raise Exception



def ReadLoopTest2(workerID):
    """
    Tests reading from multiple shared objects before and after an object value has been changed
    Changes are synchronized over several barriers
    """

    if (workerID == 0):
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    oldObj1Value = PyDOOMS.get(1).value
    oldObj2Value = PyDOOMS.get(2).value
    oldObj3Value = PyDOOMS.get(3).value

    PyDOOMS.barrier()

    if (workerID is not 0):
        PyDOOMS.barrier()
        PyDOOMS.barrier()
        PyDOOMS.barrier()

    elif (workerID == 0):
        obj1 = PyDOOMS.get(1)
        obj1.value = obj1.value + 1
        PyDOOMS.objectUpdated(obj1,"value")
        PyDOOMS.barrier()

        obj2 = PyDOOMS.get(2)
        obj2.value = obj2.value + 1
        PyDOOMS.objectUpdated(obj2,"value")
        PyDOOMS.barrier()

        obj3 = PyDOOMS.get(3)
        obj3.value = obj3.value + 1
        PyDOOMS.objectUpdated(obj3,"value")
        PyDOOMS.barrier()

    if not (oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and PyDOOMS.get(1).value == 1 and PyDOOMS.get(2).value == 1 and PyDOOMS.get(3).value == 1):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObj1Value) + "," + str(PyDOOMS.get(1).value) + " "
                         + str(oldObj2Value) + "," + str(PyDOOMS.get(2).value) + " "
                         + str(oldObj3Value) + "," + str(PyDOOMS.get(3).value) + " ")
        raise Exception



def ReadLoopTest3(workerID):
    """
    Tests reading from multiple shared objects before and after an object value has been changed.
    Changes are synchronized in one barrier
    """

    if (workerID == 0):
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    oldObj1Value = PyDOOMS.get(1).value
    oldObj2Value = PyDOOMS.get(2).value
    oldObj3Value = PyDOOMS.get(3).value

    PyDOOMS.barrier()

    if (workerID is not 0):
        PyDOOMS.barrier()

    elif (workerID == 0):
        obj1 = PyDOOMS.get(1)
        obj2 = PyDOOMS.get(2)
        obj3 = PyDOOMS.get(3)
        obj1.value = obj1.value + 1
        obj2.value = obj2.value + 1
        obj3.value = obj3.value + 1
        PyDOOMS.objectUpdated(obj1,"value")
        PyDOOMS.objectUpdated(obj2,"value")
        PyDOOMS.objectUpdated(obj3,"value")
        PyDOOMS.barrier()

    if not (oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and PyDOOMS.get(1).value == 1 and PyDOOMS.get(2).value == 1 and PyDOOMS.get(3).value == 1):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObj1Value) + "," + str(PyDOOMS.get(1).value) + " "
                         + str(oldObj2Value) + "," + str(PyDOOMS.get(2).value) + " "
                         + str(oldObj3Value) + "," + str(PyDOOMS.get(3).value) + " ")
        raise Exception



def WriteLoopTest1(workerID):
    """
    Test all nodes writing and reading to/from a single shared object, one at a time
    """
    nodes = PyDOOMS.getNumberOfNodes()

    if (workerID == 0):
        TestObject(1)

    PyDOOMS.barrier()

    oldObjValue = PyDOOMS.get(1).value

    PyDOOMS.barrier()

    for i in range(nodes):
        if (workerID == i):
            obj = PyDOOMS.get(1)
            obj.value += 1
            PyDOOMS.objectUpdated(obj,"value")
        PyDOOMS.barrier()

    if not (oldObjValue == 0 and PyDOOMS.get(1).value == nodes):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObjValue) + "," + str(PyDOOMS.get(1).value) + " ")
        raise Exception



'''def WriteLoopTest2(workerID):
    """
    Tests all nodes writing to different shared objects (one object is written by only one node)
    and all nodes reading from all shared objects
    !!! Assumes that there are 4 workers !!!
    """

    threshold = 10

    if (workerID == 0):
        TestObject(0)
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    oldObj0Value = PyDOOMS.get(0).value
    oldObj1Value = PyDOOMS.get(1).value
    oldObj2Value = PyDOOMS.get(2).value
    oldObj3Value = PyDOOMS.get(3).value

    PyDOOMS.barrier()

    while (PyDOOMS.get(workerID).value < threshold): # Doesnt work, since workers in the same node can read changes before barriers
        obj = PyDOOMS.get(workerID)
        obj.value += 1
        PyDOOMS.objectUpdated(obj,"value")
        PyDOOMS.barrier()

    if not (oldObj0Value == 0 and oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and
                PyDOOMS.get(0).value == threshold and PyDOOMS.get(1).value == threshold and PyDOOMS.get(2).value == threshold and PyDOOMS.get(3).value == threshold):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObj0Value) + "," + str(PyDOOMS.get(0).value) + " "
                         + str(oldObj1Value) + "," + str(PyDOOMS.get(1).value) + " "
                         + str(oldObj2Value) + "," + str(PyDOOMS.get(2).value) + " "
                         + str(oldObj3Value) + "," + str(PyDOOMS.get(3).value) + " ")
        raise Exception
'''


def WriteLoopTest3(workerID):
    """
    Test writing and reading to/from multiple shared object from each node
    """
    nodes = PyDOOMS.getNumberOfNodes()

    if (workerID == 0):
        TestObject(0)
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    oldObj0Value = PyDOOMS.get(0).value
    oldObj1Value = PyDOOMS.get(1).value
    oldObj2Value = PyDOOMS.get(2).value
    oldObj3Value = PyDOOMS.get(3).value

    PyDOOMS.barrier()

    for i in range(nodes):
        if (workerID == i):
            obj0 = PyDOOMS.get(0)
            obj1 = PyDOOMS.get(1)
            obj2 = PyDOOMS.get(2)
            obj3 = PyDOOMS.get(3)
            obj0.value += 1
            obj1.value += 1
            obj2.value += 1
            obj3.value += 1
            PyDOOMS.objectUpdated(obj0,"value")
            PyDOOMS.objectUpdated(obj1,"value")
            PyDOOMS.objectUpdated(obj2,"value")
            PyDOOMS.objectUpdated(obj3,"value")
        PyDOOMS.barrier()

    if not (oldObj0Value == 0 and oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and
                PyDOOMS.get(0).value == nodes and PyDOOMS.get(1).value == nodes and PyDOOMS.get(2).value == nodes and PyDOOMS.get(3).value == nodes):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObj0Value) + "," + str(PyDOOMS.get(0).value) + " "
                         + str(oldObj1Value) + "," + str(PyDOOMS.get(1).value) + " "
                         + str(oldObj2Value) + "," + str(PyDOOMS.get(2).value) + " "
                         + str(oldObj3Value) + "," + str(PyDOOMS.get(3).value) + " ")
        raise Exception



def AttributeTest1(workerID):
    """
    Tests adding a new attribute to a shared object
    """
    if (workerID == 0):
        TestObject(1)

    PyDOOMS.barrier()

    obj = PyDOOMS.get(1)

    PyDOOMS.barrier()

    if (workerID == 0):
        obj.newAttr = 2
        PyDOOMS.objectUpdated(obj,"newAttr")

    PyDOOMS.barrier()

    val = PyDOOMS.get(1).newAttr
    if not (val == 2):
        logging.critical("Worker " + str(workerID) + " Value is:"
                         + str(val))
        raise Exception



def ObjectAttributeTest1(workerID):
    """
    Tests reading from a shared object before and after object value has been changed by another node.
    The value being changed is a TestObject2 object
    """

    if (workerID == 0):
        TestObject(1)

    PyDOOMS.barrier()

    obj = PyDOOMS.get(1)
    oldObj = obj.objectAttr
    oldObjA = oldObj.a
    oldObjB = oldObj.b

    PyDOOMS.barrier()

    if (workerID == 0):
        obj.objectAttr = TestObject2()
        obj.objectAttr.a = 2
        obj.objectAttr.b = 2
        PyDOOMS.objectUpdated(obj, "objectAttr")

    PyDOOMS.barrier()
    obj = PyDOOMS.get(1)

    if not (isinstance(oldObj,TestObject2) and oldObjA == 0 and oldObjB == 1 and
            isinstance(obj, TestObject) and isinstance(obj.objectAttr,TestObject2) and obj.objectAttr.a == 2 and obj.objectAttr.b == 2):
        logging.critical("Worker " + str(workerID) + " Values are:"
                         + str(oldObjA) + "," + str(oldObjB) + " "
                         + str(PyDOOMS.get(1).objectAttr.a) + "," + str(obj.objectAttr.b))
        raise Exception



def ShutdownTest(workerID):
    """
    Test shutdown commands
    """
    # Send shutdown message to commThread
    PyDOOMS.shutdown()

    # Wait for thread to shutdown with a timeout
    PyDOOMS._comm.commThread.join(1)

    if (PyDOOMS._comm.commThread.isAlive()):
        logging.critical("isAlive(): " + str(PyDOOMS._comm.commThread.isAlive()))
        raise Exception


def BarrierTest(workerID):
    """
    Test barrier by incrementing a single value over multiple barriers
    """
    loops = 10
    increment = 1
    results = []

    if (workerID == 0):
        for i in range(PyDOOMS.getNumberOfWorkers()):
            TestObject(i)

    PyDOOMS.barrier()
    obj = PyDOOMS.get(workerID)
    PyDOOMS.barrier()

    for i in range(loops):
        results.append(obj.value)
        obj.value += increment

        PyDOOMS.objectUpdated(obj,"value")
        PyDOOMS.barrier()

    results.append(obj.value)

    if not (results[0] == 0*increment and results[1] == 1*increment and results[2] == 2*increment and
                results[3] == 3*increment and results[4] == 4*increment):
        logging.critical("Worker" + str(workerID) + ", results: " + str(results))
        raise Exception



def testSuite(workerID):
    BarrierTest(workerID)
    #logging.info("BarrierTest finished")
    reset()

    SpreadTest1(workerID)
    #logging.info("SpreadTest1 finished")
    reset()

    SpreadTest2(workerID)
    #logging.info("SpreadTest2 finished")
    reset()

    GetTest1(workerID)
    #logging.info("GetTest1 finished")
    reset()

    ReadLoopTest1(workerID)
    #logging.info("ReadLoopTest1 finished")
    reset()

    ReadLoopTest2(workerID)
    #logging.info("ReadLoopTest2 finished")
    reset()

    ReadLoopTest3(workerID)
    #logging.info("ReadLoopTest3 finished")
    reset()

    WriteLoopTest1(workerID)
    #logging.info("WriteLoopTest1 finished")
    reset()

    #WriteLoopTest2(workerID)
    #logging.info("WriteLoopTest2 finished")
    #reset()

    WriteLoopTest3(workerID)
    #logging.info("WriteLoopTest3 finished")
    reset()

    AttributeTest1(workerID)
    #logging.info("AttributeTest1 finished")
    reset()

    ObjectAttributeTest1(workerID)
    #logging.info("ObjectAttributeTest1 finished")

    ShutdownTest(workerID)
    #logging.info("ShutdownTest finished")


try:
    PyDOOMS.execute(testSuite)

    if (PyDOOMS.getNodeID() == 0):
        logging.info("All tests passed")

except Exception as e:
    logging.exception(e)
    logging.critical("Tests failed")