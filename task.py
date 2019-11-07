import os
import sys

'''
Class Activity is a representation of an activity that a 
task should complete
'''


class Activity():
    def __init__(self, *args):
        # Activity Status: initiate, request, compute, relase, and terminate
        self.status = args[0]

        # Initate
        if self.status == 'initiate':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.claim = args[3]

        # Request
        elif self.status == 'request':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.request = args[3]

        # Release
        elif self.status == 'release':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.release = args[3]

        # Computing
        elif self.status == 'compute':
            self.taskNum_ = args[1]
            self.cycleSize = args[2]

        # Terminate
        elif self.status == 'terminate':
            self.taskNum_ = args[1]


''' 
Class Task is a representation of a task, consisting 
of information about the task specifics and activities
'''


class Task():
    def __init__(self, *args):
        # > Task Attributes
        # Task can be: unstarted, running, blocked, terminated, or aborted
        self.state = "unstarted"
        self.taskNum = args[0]              # Task Number
        self.initialClaim = [0] * args[-1]  # Initial claim of resource
        self.holding = [0] * args[-1]       # Resources held by task

        # > Time attributes
        self.currentCycle = 0               # Time / Cycles taken to run current task
        self.remainingCycle = 0             # Time / Cycles remaining during computing
        self.waitTime = 0                   # Time / Cycles a task waited
        self.blockedCycle = -1              # Time / Cycle when task was blocked

        # List of activities to execute (in order)
        self.execution = []

    ''' > Functions that Change Task State'''

    # Setting Task State to unstarted
    def unstart(self):
        self.state = "unstarted"

    # Setting Task State to running and incrementing current cycle
    def run(self):
        self.state = "running"
        self.blockedCycle = -1
        self.currentCycle += 1

    # Settin Task state to blocked (it not deadlocked) and adds rejected activities into execution list
    def block(self, activity=None, deadlocked=False):
        if activity is not None:
            # need to be constnatly in front of execution list
            self.execution.inset(0, activity)
        if deadlocked == False:
            self.state = "blocked"
            if self.blockedCycle < 0:
                self.blockedCycle = self.currentCycle
            self.waitTime += 1
            self.currentCycle += 1

    # Setting Task State to terminated
    def terminate(self):
        self.state = "terminated"

    # Setting Task State to aborted
    def abort(self):
        self.state = "aborted"

    ''' > Functions for Managing Activities'''

    # Getting the next activity in execution list
    def getActivity(self):
        return self.activity.pop(0)

    # New activity added into the execution list
    def newActivity(self, activity):
        self.execution.append(activity)

    # Getting next activity's status
    def nextAcitivty(self):
        return self.execution[0].status

    ''' > Functions for Managing Task'''

    # Getting Task's Claim
    def getClaim(self, resourceType):
        return self.claim[resourceType-1]

    # Changing Claim Value
    def changeClaim(self, resourceType, value):
        self.claim[resourceType-1] = value

    # Computing Time: decrementing remaining time and increasing total time
    def updateComputeTime(self, cycleSize=None):
        if cycleSize is not None:
            self.remainingCycle = cycleSize
        self.cycleSize -= 1
        self.currentCycle += 1

    # Getting held resources and updating value of held resource
    def updateHoldResource(self, resourceType, value=-1):
        if value >= 0 and value <= self.getClaim(resourceType):
            self.holding[resourceType - 1] = value
        return self.holding[resourceType - 1]

    ''' > Checker Function'''

    # Checking whether task is computing
    def bool_compute(self):
        return self.remainingCycle > 0


'''
Class TaskList is the list of all tasks that needs to be exectued
using resource allocation algorithms (FIFO / Banker)
'''


class TaskList(list):
    def __inint__(self, allocType):
        super(TaskList, self).__init__()
        # Total number of resource Type (careful of name)
        self.resource = 0
        self.currentResource = []                   # List of current resources
        self.totalResource = []                     # List of total amount of resources

        # If statement for choosing allocation type
        if allocType == "FIFO":
            self.allocType = FIFO()                 # Running FIFO by creating FIFO instance
        elif allocType == "Banker":
            # Running Banker by creating Banker instance
            self.allocType = Banker()

    # Starting Resource Allocation
    def start(self):
        self.allocType.start(self)

    ''' > Functions Managing Activity'''

    # New activities added depending on input parameter (task number)
    def newActivity(self, *specs):
        activity = Activity(*specs)
        # CHECKED: activity and activity num correct
        # PROBLEM: self.taskByNum(activity.taskNum_) returning string
        self.taskByNum(activity.taskNum_).newActivity(activity)
        
    ''' > Functions Managing Tasks'''

    # New tasks created with input parameter & appended to taskList
    def newTask(self, *specs):
        # checked
        self.append(Task(*specs, self.resource))

    # Retrieving tasks by taskNum
    def taskByNum(self, taskNum):
        print("This is the result:",self)
        return self[taskNum-1]

    # Retrieving tasks in particular state
    def taskByState(self, tState):
        tasks = []
        for task in self:
            if task.state == tState:
                tasks.append(task)
        return tasks

    ''' > Functions Managing Resources'''
    # Getting held resources and updating value of held resource

    def updateHoldResource(self, resourceType, value=-1):
        if value >= 0:
            self.currentResource[resourceType - 1] = value
        return self.currentResource[resourceType - 1]

    # Responds to task request through resource allocation
    def allocate(self, task, resourceType, value):
        # Updating Task Resource
        taskResource = task.updateHoldResource(resourceType)
        task.updateHoldResource(resourceType, taskResource + value)

        # Update TaskList
        heldResource = self.updateHoldResource(resourceType)
        self.updateHoldResource(resourceType, heldResource - value)

    # Release resource when told to release
    def release(self, task, resourceType=None, value=None):
        if resourceType is not None and value is not None:
            # Updating Task Resource
            taskResource = task.updateHoldResource(resourceType)
            task.updateHoldResource(resourceType, taskResource - value)

            # Update TaskList
            heldResource = self.updateHoldResource(resourceType)
            self.updateHoldResource(resourceType, heldResource + value)
        else:
            # To release all of the resource
            for i in range(1, 1+self.resource):
                self.updateHoldResource(i, self.updateHoldResource(
                    i) + task.updateHoldResource(i))

    ''' > Checker Functions'''

    # Boolean that checks whether resource can be allocated
    def bool_allocate(self, resourceType, value):
        if self.updateHoldResource(resourceType) - value >= 0:
            return True
        else:
            return False

    # Boolean that checks whether task is terminated
    def bool_terminated(self):
        totalTerminated = len(self.taskByState("terminated"))
        totalAborted = len(self.taskByState("aborted"))
        if totalTerminated + totalAborted < len(self):
            return False
        else:
            return True

    # Boolean that checks whether state is safe (Banker's Algo)
    # Safe means all requests can be satisfied
    def bool_safe(self, task):
        for i in range(1, self.resourceType+1):
            if task.getClaim(i) - task.updateHoldResource(i) > self.updateHoldResource(i):
                return False
        return True

    # Boolean that checks for deadlocks
    # Deadlock means that unfinished tasks are blocked due to allocation problems (no requests can be further satisfied)
    def bool_deadlock(self):
        running = self.taskByState('running')
        blocked = self.taskByState('blocked')
        if len(running) > 0 or len(blocked) == 0:
            return False
        for bt in blocked:
            activity = bt.getActivity()
            bt.block(activity, deadlocked=True)
            if self.bool_allocate(activity.resourceType, activity.claim):
                return False

        return True

    ''' > Utility Function'''

    def printResult(self):
        print(self.allocType)
        cycleSum = 0
        waitSum = 0
        for task in self:
            if task.state == "aborted":
                print("Task {}:\t{}".format(task.taskNum, task.state))
            else:
                print("Task {}:\t{}\t{}\t{}%".format(
                    task.taskNum, task.currentCycle, task.waitTime, task.waitTime/task.currentCycle * 100))
                cycleSum += task.currentCycle
                waitSum += task.waitTime
        print("Total:\t{}\t{}\t{}%".format(
            cycleSum, waitSum, waitSum/cycleSum * 100))


'''
Class FIFO is a simulation of the optimistic resource manager that processes tasks in FIFO
'''


class FIFO():
    def __init__(self, *args):
        self.argument = args
        self.type = "FIFO"

    def start(self, taskManager):
        print("FIFO STARTED")
        
        # Once all tasks are finished (terminated), the result is printed
        if taskManager.bool_terminated():
            taskManager.printResult()
            return
        
        # Step 1: Check blocked tasks to determine whether allocation is possible
        blocked = taskManager.taskByState("blocked")
        blocked.sort(key=lambda task: task.blockedCycle)
        for i in blocked:
            activity = i.getActivity()
            if taskManager.bool_allocate(activity.resourceType, activity.claim):
                taskManager.allocate(i, activity.resourceType, activity.claim)
                i.unstart()
            else:
                i.block(activity)

        # Step 2: Check running tasks. If computing, let it compute. If not, process
        running = taskManager.taskByState("running")
        releasedResource = []
        for i in running:
            if i.bool_compute():
                i.updateComputeTime()
                continue
            activity = i.getActiviy()
            # request compute release terminate

            if activity.status == "request":
                # Check whether the resource can be allocated.
                if taskManager.bool_allocate(activity.resourceType, activity.request):
                    taskManager.allocate(
                        i, activity.resourceType, activity.request)
                    i.run()
                else:
                    i.block(activity)
            # When Activity status is released, release
            elif activity.status == "release":
                releasedResource.append(
                    [i, activity.resourceType, activity.relase])
                i.run()
            # When Activity status is compute, update compute time
            elif activity.status == "compute":
                i.updateComputeTime(activity.cycleSize)
            # When Activity status is terminate, terminate
            elif activity.status == "terminate":
                i.terminate()
        for released in releasedResource:
            taskManager.release(*released)

        # Step 3: Starting unstarted tasks
        unstarted = taskManager.taskByState("unstarted")
        for i in unstarted:
            if i.nextAcitivty() == "initiate":
                activity = i.getActivity()
                i.changeClaim(activity.resourceType, activity.claim)
            i.run()

            # If next activity is still intiate, unstart
            if i.nextActivity() == "initiate":
                i.unstart()

        # Dealing with deadlocks
        while taskManager.bool_deadlock():
            # while deadlocked, aborting tasks
            abortTask = taskManager.taskByState("blocked")[0]
            abortTask.abort()
            taskManager.release(abortTask)

        self.start(taskManager)


'''
Class Banker is a simulation of Banker Algorithm (resource manager)
'''


class Banker():
    def __init__(self, *args):
        self.argument = args
        self.type = "Banker"

    def start(self, taskManager):
        # Once all tasks are finished (terminated), the result is printed
        if taskManager.bool_terminated():
            taskManager.printResult()
            return
        # Step 1: Check blocked tasks to determine whether allocation is safe
        blocked = taskManager.taskByState("blocked")
        blocked.sort(key=lambda task: task.blockedCycle)
        for i in blocked:
            activity = i.getActivity()
            # Check safety before allocation
            if taskManager.bool_safe(i):
                taskManager.allocate(
                    i, activity.resourceType, activity.request)
                i.unstart()
            # If unsafe, block
            else:
                i.block(activity)

        # Step 2: Check running tasks. If computing, let it compute. If not, process
        running = taskManager.taskByState("running")
        releasedResource = []
        for i in running:
            if i.bool_compute():
                i.updateComputeTime()
                continue
            activity = i.getActiviy()

            # request compute release terminate
            if activity.status == "request":
                # If held resources + requested resources is larger than the claim, abort task
                if i.getClaim(activity.resourceType) < i.updateHoldResource(activity.resourceType) + activity.request:
                    # print message
                    print('During cycle {}-{} of Banker\'s algorithms\n\tTask {}\'s request exceeds its claim; aborted;'.format(
                        i.currentCycle, i.currentCycle + 1, i.taskNum))
                    i.abort()
                    taskManager.release(i)

                # If allocation is safe, allocate resources
                elif taskManager.bool_safe(i):
                    taskManager.allocate(
                        i, activity.resourceType, activity.request)
                    i.run()

                # If unsafe, block
                else:
                    i.block()

            # When Activity status is released, release
            elif activity.status == "release":
                releasedResource.append(
                    [i, activity.resourceType, activity.relase])
                i.run()
            # When Activity status is compute, update compute time
            elif activity.status == "compute":
                i.updateComputeTime(activity.cycleSize)
            # When Activity status is terminate, terminate
            elif activity.status == "terminate":
                i.terminate()
        for released in releasedResource:
            taskManager.release(*released)

        # Step 3: Starting unstarted tasks
        unstarted = taskManager.taskByState("unstarted")
        for i in unstarted:
            if i.nextAcitivty() == "initiate":
                activity = i.getActivity()

                if taskManager.bool_allocate(activity.resourceType, activity.claim):
                    i.changeclaim(activity.resourceType, activity.claim)
                else:
                    # print abort statement
                    print('Banker aborts task {} before run begins:\n\tclaim for resource {} ({}) exceeds number of units present ({})'.format(
                        i.status, activity.resourceType, activity.claim, taskManager.updateHoldResource(activity.resourceType)))
                    i.abort()
                    continue
            i.run()
            if i.nextActivity() == "initiate":
                i.unstart()

        self.start(taskManager)


'''
Main function - running the resource allocators (FIFO and Banker)
'''


def main():
    if len(sys.argv[1]) < 1:
        print("Input file is required")

    inputFile = sys.argv[1]

    # Running FIFO
    
    runFifo = TaskList('FIFO')
    
    # Error Message if wrong file name or if file does not exist
    if not os.path.isfile(inputFile):
        print("Input file does not exist. Please Restart.")
        return
    # Receieve and organize Input File
    with open(inputFile, "r") as File:
        operations = []
        for line in File:
            # for element in line.strip().split():
            #     if element.isnumeric():
            #         operations.append(int(element))
            operations += [int(element) if element.isnumeric() else element for element in line.strip().split()]
    
    # CHECKED: operations

    T = operations.pop(0)
    R = operations.pop(0)
    
    # CHECKED: T,R

    runFifo.resource = R
    unit = operations[:R]
    
    operations = operations[R:]


    for num in range(1, T+1):
        runFifo.newTask(num)
    
    # CHECKED: appending new task

    runFifo.currentResource = unit
    runFifo.totalResource = unit

    # CHECKED: operation and its length

    while len(operations) > 0:
        runFifo.newActivity(*operations[:4])
        operations = operations[4:]
    
    runFifo.start()
    
    # Run Banker

    runBanker = TaskList('Banker')

    # Error Message if wrong file name or if file does not exist
    if not os.path.isfile(inputFile):
        print("Input file does not exist. Please Restart.")
        return

    # Receieve and organize Input File
    with open(inputFile, "r") as File:
        operations = []
        for line in File:
            # for element in line.strip().split():
            #     if element.isnumeric():
            #         operations.append(int(element))
            operations += [int(element) if element.isnumeric() else element for element in line.strip().split()]
    
    T = operations.pop(0)
    R = operations.pop(0)
    runBanker.resource = R
    unit = operations[:R]
    tokens = operations[R:]

    for num in range(1, T+1):
        runBanker.newTask(num)
    runBanker.currentResource = unit
    runBanker.totalResource = unit

    while len(operations) > 0:
        runBanker.newActivity(+operations[:5])
        operations = operations[5:]

    runBanker.start()


if __name__ == "__main__":
    main()

