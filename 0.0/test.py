import SharedObject
import random, math, time, sys
import logging

myname = eval(sys.argv[1])


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d (%(threadName)-2s) %(message)s',datefmt='%M:%S'
                    )

class TestObject(SharedObject.SharedObject):
    def __init__(self, ID):
        SharedObject.SharedObject.__init__(self, ID)
        self.value = 0


def printDict():
    objects = SharedObject.manager.objects
    print "--------------- Process:",myname,"--------------------------------------------"
    for element in objects:
        if (isinstance(objects[element][0],TestObject)):
            print element,"  -  ", objects[element]


# Test spreading references of objects residing in Process 0
# Process 0 should have all objects in its dict, other processes should only have references to all objects
def SpreadTest1():

    if (myname == 0):
        TestObject(1)
        TestObject(2)
        TestObject(3)
        TestObject(4)

    time.sleep(0.1) # wait for references to spread

    printDict()
    logging.debug("Process " + str(myname) + " SpreadTest1 finished")


# Test spreading references of objects residing in several different processes
# Process n should have object n in its dict, and only references to all other objects
def SpreadTest2():
    if (myname == 0):
        TestObject(0)
    elif (myname == 1):
        TestObject(1)
    elif (myname == 2):
        TestObject(2)
    elif (myname == 3):
        TestObject(3)

    time.sleep(0.2) # wait for references to spread
    printDict()
    logging.debug("Process " + str(myname) + " SpreadTest2 finished")


# Test spreading references of objects residing in all processes (every process has a copy of every object)
# Each object should be writable in only one process, and readable in all others
def SpreadTest3():

    TestObject(1)
    TestObject(2)
    TestObject(3)
    TestObject(4)
    TestObject(5)
    TestObject(6)
    TestObject(7)
    TestObject(8)

    time.sleep(0.1) # wait for references to spread
    printDict()
    logging.debug("Process " + str(myname) + " SpreadTest3 finished")


# Test reading from remote object by doing a busy-wait for attribute change
def ReadLoopTest1():

    if (myname == 0):
        obj = TestObject(1)

    time.sleep(0.2) # wait for references to spread

    logging.debug("Process " + str(myname) + " Value is " + str(SharedObject.get(1).value))
    if (myname == 0):
        SharedObject.get(1).value += 1
    logging.debug("Process " + str(myname) + " Value is " + str(SharedObject.get(1).value))
    SharedObject.barrier()
    logging.debug("Process " + str(myname) + " Value is " + str(SharedObject.get(1).value))


    printDict()
    logging.debug("Process " + str(myname) + " ReadLoopTest1 finished")



# Test reading from multiple remote object (one object is checked in each process) by doing a busy-wait for attribute change
def ReadLoopTest2():

    if (myname == 0):
        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)

    time.sleep(0.1) # wait for references to spread

    if (myname is not 0):
        while (SharedObject.get(myname,Communication.READ_ACCESS).value == 0):
            logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) + ": Value is 0")
            time.sleep(0.5)
        logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) +
                      ", Value is " + str(SharedObject.get(myname,Communication.READ_ACCESS).value))
    elif (myname == 0):
        time.sleep(1)
        obj1.value = obj1.value + 1
        logging.debug("Process " + str(myname) + " Object 1 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(1) # invalidate all copies of this object

        time.sleep(1)
        obj2.value = obj2.value + 1
        logging.debug("Process " + str(myname) + " Object 2 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(2) # invalidate all copies of this object

        time.sleep(1)
        obj3.value = obj3.value + 1
        logging.debug("Process " + str(myname) + " Object 3 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(3) # invalidate all copies of this object

    printDict()
    logging.debug("Process " + str(myname) + " ReadLoopTest2 finished")



# Test reading from multiple remote object from each process by doing a busy-wait for attribute change
def ReadLoopTest3():

    if (myname == 0):
        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)
        obj4 = TestObject(4)

    SharedObject.barrier()
    time.sleep(0.1) # wait for references to spread

    if (myname is not 0):
        while (SharedObject.get(myname,Communication.READ_ACCESS).value == 0 or
                       SharedObject.get(myname+1,Communication.READ_ACCESS).value == 0):
            logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) +
                      ", Value is " + str(SharedObject.get(myname,Communication.READ_ACCESS).value) +
                ", Retrieved object" + str(myname+1) + ", Value is" + str(SharedObject.get(myname+1,Communication.READ_ACCESS).value))
            time.sleep(0.4)
        logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) +
                      ", Value is " + str(SharedObject.get(myname,Communication.READ_ACCESS).value))
    elif (myname == 0):
        time.sleep(1)
        obj1.value = obj1.value + 1
        logging.debug("Process " + str(myname) + " Object 1 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(1) # invalidate all copies of this object

        time.sleep(1)
        obj2.value = obj2.value + 1
        logging.debug("Process " + str(myname) + " Object 2 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(2) # invalidate all copies of this object

        time.sleep(1)
        obj3.value = obj3.value + 1
        logging.debug("Process " + str(myname) + " Object 3 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(3) # invalidate all copies of this object

        time.sleep(1)
        obj4.value = obj4.value + 1
        logging.debug("Process " + str(myname) + " Object 4 updated, invalidating")
        SharedObject.pydooms_sendInvalidate(4) # invalidate all copies of this object

    printDict()
    logging.debug("Process " + str(myname) + " ReadLoopTest3 finished")



# Test all processes writing to a single remote object
def WriteLoopTest1():

    if (myname == 0):
        obj = TestObject(1)

    SharedObject.barrier()
    time.sleep(0.1) # wait for references to spread
    logging.debug("Process " + str(myname) + " Starting WriteLoopTest1")

    while (SharedObject.get(1,Communication.READ_ACCESS).value < 6):
        obj = SharedObject.get(1,Communication.WRITE_ACCESS)
        logging.debug("Process "+str(myname) + " retrieved object 1: Value is " + str(obj.value))
        logging.debug("Process "+str(myname) + " incrementing value")
        obj.value += 1
        logging.debug("Process "+str(myname) + " sending invalidate")
        SharedObject.pydooms_sendInvalidate(1)
        time.sleep(0.5) # Wait so all nodes have a chance of getting the write lock
    logging.debug("Process " + str(myname) + " Retrieved object 1" +
                      ": Value is " + str(SharedObject.get(1,Communication.READ_ACCESS).value))
    SharedObject.barrier()
    printDict()
    logging.debug("Process " + str(myname) + " WriteLoopTest1 finished")


# Test writing to multiple remote object (one object is written by only one process)
def WriteLoopTest2():

    if (myname == 0):
        obj0 = TestObject(0)
        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)

    SharedObject.barrier()
    time.sleep(0.1) # wait for references to spread

    while (SharedObject.get(myname,Communication.READ_ACCESS).value < 4):
        obj = SharedObject.get(myname,Communication.WRITE_ACCESS)
        logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) + ": Value is " + str(obj.value))
        logging.debug("Process " + str(myname) + " Incrementing value")
        obj.value += 1
        SharedObject.pydooms_sendInvalidate(myname)
        time.sleep(0.5)
    logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) +
                      ", Value is " + str(SharedObject.get(myname,Communication.READ_ACCESS).value))

    SharedObject.barrier()
    printDict()
    logging.debug("Process " + str(myname) + " WriteLoopTest2 finished")



# Test writing to multiple remote object from each process
def WriteLoopTest3():

    if (myname == 0):
        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)
        obj4 = TestObject(4)

    SharedObject.barrier()
    time.sleep(0.1) # wait for references to spread


    while (SharedObject.get(myname,Communication.READ_ACCESS).value <= 30 or
                   SharedObject.get(myname+1,Communication.READ_ACCESS).value <= 30):
        obja = SharedObject.get(myname,Communication.WRITE_ACCESS)
        objb = SharedObject.get(myname+1,Communication.WRITE_ACCESS)
        logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) + ": Value is " + str(obja.value) +
                      ", object " + str(myname+1) + ": Value is " + str(objb.value))
        logging.debug("Process " + str(myname) + " Incrementing values")
        obja.value += 1
        objb.value += 1
        SharedObject.pydooms_sendInvalidate(myname)
        SharedObject.pydooms_sendInvalidate(myname+1)
        time.sleep(0.5)

    logging.debug("Process " + str(myname) + " Retrieved object " + str(myname) +
                  ", Value is " + str(SharedObject.get(myname,Communication.READ_ACCESS).value) + ", Retrieved object" +
                  str(myname+1) + ", Value is" + str(SharedObject.get(myname+1,Communication.READ_ACCESS).value))

    SharedObject.barrier()
    printDict()
    logging.debug("Process " + str(myname) + " WriteLoopTest3 finished")



#SpreadTest1()
#SpreadTest2()
#SpreadTest3()  # Not implemented
ReadLoopTest1()
#ReadLoopTest2()
#ReadLoopTest3()
#WriteLoopTest1() # Not data-race-free
#WriteLoopTest2()
#WriteLoopTest3() # Not data-race-free
#MergeUpdateTEst