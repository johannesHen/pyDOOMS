"""
Module containing basic tests for different aspects of the PyDOOMS library
At the moment most test assumes that there are 4 nodes running
"""

import sys, os, time
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import PyDOOMS
from TestObject import TestObject


myname = eval(sys.argv[1])

def printDict():
    """
    Prints the contents of the object store in a node.
    """
    objects = PyDOOMS._store.objects
    print "-------------------------------------Process: ",myname," --------------------------------------------"
    for element in objects:
        if (isinstance(objects[element],TestObject)):
            print element,"  -  ", objects[element]



def reset():
    """
    Reset the testing environment.
    Barrier is needed to stop messages received from nodes already in the next test being removed
    """
    PyDOOMS._reset()
    PyDOOMS.barrier()



def SpreadTest1():
    """
    Tests creation and spreading of objects residing in node 0
    All nodes should have all objects in their local object store
    """
    numOfObj = 500

    if (myname == 0):
        for i in range(numOfObj):
            TestObject(i)

    PyDOOMS.barrier()
    # The python dictionary appears to do non-blocking non-immediate inserts into the object store dict.
    # Our PyDOOMS.get() function will wait for inserts to be made, but when checking the length of the dict
    # (which should never be done outside perhaps testing) we must first wait for all inserts to complete
    time.sleep(0.0001)

    if (len(PyDOOMS._store.objects) != numOfObj):
        logging.critical("Process " + str(myname) + " Number of objects:" + str(len(PyDOOMS._store.objects)))
        printDict()
        raise Exception



def SpreadTest2():
    """
    Tests creation and spreading of objects residing in several different processes
    All nodes should have all objects in their local object store
    """

    for i in range(nodes):
        if (myname == i):
            for i in range(i*100,i*100+100):
                TestObject(i)

    PyDOOMS.barrier()
    # The python dictionary appears to do non-blocking non-immediate inserts into the object store dict.
    # Our PyDOOMS.get() function will wait for inserts to be made, but when checking the length of the dict
    # we must first wait for all inserts to complete
    time.sleep(0.0001)

    if (len(PyDOOMS._store.objects) != 400):
        logging.critical("Process " + str(myname) + " Number of objects:" + str(len(PyDOOMS._store.objects)))
        printDict()
        raise Exception



def GetTest1():
    """
    Tests retrieving object references from local object store and accessing objects
    """
    numOfObj = 100

    if (myname == 0):
        for i in range(numOfObj):
            TestObject(i)

    PyDOOMS.barrier()

    for i in range(numOfObj):
        PyDOOMS.get(i).value

    #logging.debug("Process " + str(myname) + " GetTest 1 finished successfully")



def ReadLoopTest1():
    """
    Tests reading from a shared object before and after object value has been changed by another node
    """

    if (myname == 0):
        TestObject(1)

    PyDOOMS.barrier()

    obj = PyDOOMS.get(1)
    oldValue = obj.value

    if (myname == 0):
        obj.value = 1
        PyDOOMS._comm.addOutgoingUpdate(1, "value", obj.value)

    PyDOOMS.barrier()

    if not (oldValue == 0 and obj.value == 1):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldValue) + "," + str(obj.value) + " ")
        raise Exception



def ReadLoopTest2():
    """
    Tests reading from multiple shard objects by doing a busy-wait for attribute change
    Changes are synchronized over several barriers
    """

    if (myname == 0):
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    obj1 = PyDOOMS.get(1)
    obj2 = PyDOOMS.get(2)
    obj3 = PyDOOMS.get(3)
    oldObj1Value = obj1.value
    oldObj2Value = obj2.value
    oldObj3Value = obj3.value


    if (myname is not 0):
        while (obj1.value == 0 or obj2.value == 0 or obj3.value == 0):
            PyDOOMS.barrier()

    elif (myname == 0):
        obj1.value = obj1.value + 1
        PyDOOMS._comm.addOutgoingUpdate(1,"value",1)
        PyDOOMS.barrier()

        obj2.value = obj2.value + 1
        PyDOOMS._comm.addOutgoingUpdate(2,"value",1)
        PyDOOMS.barrier()

        obj3.value = obj3.value + 1
        PyDOOMS._comm.addOutgoingUpdate(3,"value",1)
        PyDOOMS.barrier()

    if not (oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and obj1.value == 1 and obj2.value == 1 and obj3.value == 1):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldObj1Value) + "," + str(obj1.value) + " "
                         + str(oldObj2Value) + "," + str(obj2.value) + " "
                         + str(oldObj3Value) + "," + str(obj3.value) + " ")
        raise Exception



def ReadLoopTest3():
    """
    Tests reading from multiple shard objects by doing a busy-wait for attribute change
    Changes are synchronized in one barrier
    """

    if (myname == 0):
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    obj1 = PyDOOMS.get(1)
    obj2 = PyDOOMS.get(2)
    obj3 = PyDOOMS.get(3)
    oldObj1Value = obj1.value
    oldObj2Value = obj2.value
    oldObj3Value = obj3.value


    if (myname is not 0):
        while (obj1.value == 0 or obj2.value == 0 or obj3.value == 0):
            PyDOOMS.barrier()

    elif (myname == 0):
        obj1.value = obj1.value + 1
        obj2.value = obj2.value + 1
        obj3.value = obj3.value + 1
        PyDOOMS._comm.addOutgoingUpdate(1,"value",1)
        PyDOOMS._comm.addOutgoingUpdate(2,"value",1)
        PyDOOMS._comm.addOutgoingUpdate(3,"value",1)
        PyDOOMS.barrier()

    if not (oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and obj1.value == 1 and obj2.value == 1 and obj3.value == 1):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldObj1Value) + "," + str(obj1.value) + " "
                         + str(oldObj2Value) + "," + str(obj2.value) + " "
                         + str(oldObj3Value) + "," + str(obj3.value) + " ")
        raise Exception



def WriteLoopTest1():
    """
    Test all nodes writing and reading to/from a single shared object, one at a time
    """

    if (myname == 0):
        TestObject(1)

    PyDOOMS.barrier()

    obj = PyDOOMS.get(1)
    oldObjValue = obj.value

    for i in range(nodes):
        if (myname == i):
            obj.value += 1
            PyDOOMS._comm.addOutgoingUpdate(1,"value",obj.value)
        PyDOOMS.barrier()

    if not (oldObjValue == 0 and obj.value == 4):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldObjValue) + "," + str(obj.value) + " ")
        raise Exception



def WriteLoopTest2():
    """
    Tests all nodes writing to different shared objects (one object is written by only one node)
    and all nodes reading from all shared objects
    """

    threshold = 10

    if (myname == 0):
        TestObject(0)
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    obj0 = PyDOOMS.get(0)
    obj1 = PyDOOMS.get(1)
    obj2 = PyDOOMS.get(2)
    obj3 = PyDOOMS.get(3)
    oldObj0Value = obj0.value
    oldObj1Value = obj1.value
    oldObj2Value = obj2.value
    oldObj3Value = obj3.value

    while (PyDOOMS.get(myname).value < threshold):
        obj = PyDOOMS.get(myname)
        obj.value += 1
        PyDOOMS._comm.addOutgoingUpdate(myname,"value",obj.value)
        PyDOOMS.barrier()

    if not (oldObj0Value == 0 and oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and
                obj0.value == threshold and obj1.value == threshold and obj2.value == threshold and obj3.value == threshold):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldObj0Value) + "," + str(obj0.value) + " "
                         + str(oldObj1Value) + "," + str(obj1.value) + " "
                         + str(oldObj2Value) + "," + str(obj2.value) + " "
                         + str(oldObj3Value) + "," + str(obj3.value) + " ")
        raise Exception



def WriteLoopTest3():
    """
    Test writing and reading to/from multiple shared object from each node
    """

    if (myname == 0):
        TestObject(0)
        TestObject(1)
        TestObject(2)
        TestObject(3)

    PyDOOMS.barrier()

    obj0 = PyDOOMS.get(0)
    obj1 = PyDOOMS.get(1)
    obj2 = PyDOOMS.get(2)
    obj3 = PyDOOMS.get(3)
    oldObj0Value = obj0.value
    oldObj1Value = obj1.value
    oldObj2Value = obj2.value
    oldObj3Value = obj3.value

    for i in range(4):
        if (myname == i):
            obj0.value += 1
            obj1.value += 1
            obj2.value += 1
            obj3.value += 1
            PyDOOMS._comm.addOutgoingUpdate(obj0.ID,"value",obj0.value)
            PyDOOMS._comm.addOutgoingUpdate(obj1.ID,"value",obj1.value)
            PyDOOMS._comm.addOutgoingUpdate(obj2.ID,"value",obj2.value)
            PyDOOMS._comm.addOutgoingUpdate(obj3.ID,"value",obj3.value)
        PyDOOMS.barrier()

    if not (oldObj0Value == 0 and oldObj1Value == 0 and oldObj2Value == 0 and oldObj3Value == 0 and
                obj0.value == 4 and obj1.value == 4 and obj2.value == 4 and obj3.value == 4):
        logging.critical("Process " + str(myname) + " Values are:"
                         + str(oldObj0Value) + "," + str(obj0.value) + " "
                         + str(oldObj1Value) + "," + str(obj1.value) + " "
                         + str(oldObj2Value) + "," + str(obj2.value) + " "
                         + str(oldObj3Value) + "," + str(obj3.value) + " ")
        raise Exception



def ShutdownTest():
    """
    Test shutdown commands
    """
    # Send several shutdown messages to commThread
    PyDOOMS.shutdown()
    PyDOOMS.shutdown()
    PyDOOMS.shutdown()

    # Restart commThread
    PyDOOMS._reset()

    # commThread should be alive
    if not (PyDOOMS._comm.commThread.isAlive()):
        logging.critical("isAlive(): " + str(PyDOOMS._comm.commThread.isAlive()))
        raise Exception



def BarrierTest():
    """
    Test barrier by incrementing a single value over multiple barriers
    """
    loops = 10
    increment = 1
    results = []

    if (myname == 0):
        for i in range(nodes):
            TestObject(i)

    PyDOOMS.barrier()
    obj = PyDOOMS.get(myname)

    for i in range(loops):
        results.append(obj.value)
        obj.value += increment

        PyDOOMS._comm.addOutgoingUpdate(obj.ID,"value",obj.value)
        PyDOOMS.barrier()

    results.append(obj.value)

    if not (results[0] == 0*increment and results[1] == 1*increment and results[2] == 2*increment and
                results[3] == 3*increment and results[4] == 4*increment):
        logging.critical("results: " + str(results))
        raise Exception



# ARGUMENTS
nodes = 4
testLoops = 10000

try:
    for i in range(testLoops):
        BarrierTest()
        reset()

        SpreadTest1()
        reset()

        SpreadTest2()
        reset()

        GetTest1()
        reset()

        ReadLoopTest1()
        reset()

        ReadLoopTest2()
        reset()

        ReadLoopTest3()
        reset()

        """WriteLoopTest1()
        reset()

        WriteLoopTest2()
        reset()

        WriteLoopTest3()
        reset()"""

        if (myname == 0):
            logging.debug("Test loop " + str(i+1) + " finished successfully")


except Exception as e:
    logging.exception(e)
    logging.critical("Tests failed")

finally:
    ShutdownTest()

    if (myname == 0):
        logging.info("All tests passed")

    PyDOOMS.shutdown()