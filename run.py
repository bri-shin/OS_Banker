import os
import sys

'''
The goal of this lab is to do resource allocation using both an optimistic resource manager and the banker’s algorithm of Dijkstra. The optimistic resource manager is simple: Satisfy a request if possible, if not make the task wait; when a release occurs, try to satisfy pending requests in a FIFO manner.

This program is composed of:

(Task Manager Componenets)
- Activity Class
- Task Class
- Task List Class

(Resource Allocation Methods)
- FIFO Class
- Banker Algo Class
'''



'''
Class Activity is a representation of an activity that a task should complete
'''

class Activity():
    def __init__(self, *args):
        # Activity Status: initiate, request, compute, release, and terminate
        self.status = args[0]

        # Parsing Input Command when activity status = Initate
        if self.status == 'initiate':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.claim = args[3]

        # Parsing Input Command when activity status = Request
        elif self.status == 'request':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.request = args[3]

        # Parsing Input Command when activity status = Release
        elif self.status == 'release':
            self.taskNum_ = args[1]
            self.resourceType = args[2]
            self.release = args[3]

        # Parsing Input Command when activity status = Computing
        elif self.status == 'compute':
            self.taskNum_ = args[1]
            self.cycleSize = args[2]

        # Parsing Input Command when activity status = Terminate
        elif self.status == 'terminate':
            self.taskNum_ = args[1]


''' 
Class Task is a representation of a task, consisting of information about the task specifics and activities
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
        # print("This is SELF,",self, self.getActivity().status)
        if activity is not None:
            # need to be constnatly in front of execution list          
            self.execution.insert(0, activity)

        # If not deadlock, state is set to block and the cycle and wait time are incremented
        if not deadlocked:
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
        return self.execution.pop(0)

    # New activity added into the execution list
    def newActivity(self, activity):
        self.execution.append(activity)

    # Getting next activity's status
    def nextActivity(self):
        return self.execution[0].status

    ''' > Functions for Managing Task'''

    # Getting Task's Claim
    def getClaim(self, resourceType):
        return self.initialClaim[resourceType-1]

    # Changing Claim Value
    def changeClaim(self, resourceType, value):
        self.initialClaim[resourceType-1] = value

    # Computing Time: decrementing remaining time and increasing total time
    def updateComputeTime(self, cycleSize=None):
        if cycleSize is not None:
            self.remainingCycle = cycleSize
        self.remainingCycle -= 1
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
    def __init__(self, allocType):
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
            # Update TaskList
            heldResource = self.updateHoldResource(resourceType)
            self.updateHoldResource(resourceType, heldResource + value)

            # Updating Task Resource
            taskResource = task.updateHoldResource(resourceType)
            task.updateHoldResource(resourceType, taskResource - value)
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
        for i in range(1, self.resource+1):
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
            if self.bool_allocate(activity.resourceType, activity.request):
                return False

        return True

    ''' > Utility Function'''

    def printResult(self):
        print(self.allocType.type)
        cycleSum = 0
        waitSum = 0
        for task in self:
            if task.state == "aborted":
                print("Task {}:\t{}".format(task.taskNum, task.state))
            else:
                print("Task {}:\t{}\t{}\t{}%".format(
                    task.taskNum, task.currentCycle, task.waitTime, round(task.waitTime/task.currentCycle * 100)))
                cycleSum += task.currentCycle
                waitSum += task.waitTime
        print("Total:\t{}\t{}\t{}%".format(
            cycleSum, waitSum, round(waitSum/cycleSum * 100)))
        print()


'''
Class FIFO is a simulation of the optimistic resource manager that processes tasks in FIFO
'''

class FIFO():
    def __init__(self, *args):
        self.type = "FIFO"
        self.argument = args
        
    def start(self, taskManager):
        # print("FIFO STARTED")
        
        # Once all tasks are finished (terminated), the result is printed
        if taskManager.bool_terminated():
            taskManager.printResult()
            return
        
        # Step 1: Check blocked tasks to determine whether allocation is possible
        blocked = taskManager.taskByState("blocked")
        blocked.sort(key=lambda task: task.blockedCycle)
        for i in blocked:
            activity = i.getActivity()
            if taskManager.bool_allocate(activity.resourceType, activity.request):
                taskManager.allocate(i, activity.resourceType, activity.request)
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
            activity = i.getActivity()
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
                    [i, activity.resourceType, activity.release])
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
            if i.nextActivity() == "initiate":
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
        self.type = "BANKER'S"
        self.argument = args

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
                # print("THIS IS ACTIVITY STATUS:",activity.status) -- release
                taskManager.allocate(
                    i, activity.resourceType, activity.request)
                i.unstart()
            # If unsafe, block
            else:
                i.block(activity)

        # List holding release resources
        releasedResource = []                   
        # Step 2: Check running tasks. If computing, let it compute. If not, process
        running = taskManager.taskByState("running")
        for i in running:
            if i.bool_compute():
                i.updateComputeTime()
                continue
            activity = i.getActivity()
            # request compute release terminate
            if activity.status == "request":
                # If held resources + requested resources is larger than the claim, abort task
                if i.getClaim(activity.resourceType) < i.updateHoldResource(activity.resourceType) + activity.request:
                    # print message
                    print('During cycle {}-{} of Banker\'s algorithms\n\tTask {}\'s request exceeds its claim; aborted;{} units available next cycle'.format(
                        i.currentCycle, i.currentCycle + 1, i.taskNum, activity.request))
                    i.abort()
                    taskManager.release(i)

                # If allocation is safe, allocate resources
                elif taskManager.bool_safe(i):
                    taskManager.allocate(
                        i, activity.resourceType, activity.request)
                    i.run()

                # If unsafe, block
                else:
                    # print("THIS IS BEFORE BLOCK:", activity)
                    i.block(activity)

            # When Activity status is released, release
            elif activity.status == "release":
                releasedResource.append(
                    [i, activity.resourceType, activity.release])
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
            if i.nextActivity() == "initiate":
                activity = i.getActivity()

                if taskManager.bool_allocate(activity.resourceType, activity.claim):
                    i.changeClaim(activity.resourceType, activity.claim)
                else:
                    # print abort statement
                    print('Banker aborts task {} before run begins:\n\tclaim for resource {} ({}) exceeds number of units present ({})'.format(
                        i.state, activity.resourceType, activity.claim, taskManager.updateHoldResource(activity.resourceType)))
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
    # Receieve and organize/parse Input File
    with open(inputFile, "r") as File:
        fifo_operations = []
        for line in File:
            fifo_operations += [int(fifo_element) if fifo_element.isnumeric() else fifo_element for fifo_element in line.strip().split()]
    
    # fifo_T is the number of tasks
    fifo_T = fifo_operations.pop(0)

    # fifo_R is the number of resource types
    fifo_R = fifo_operations.pop(0)
    runFifo.resource = fifo_R

    # Number of units presents of each resource type 
    fifo_unit = fifo_operations[:fifo_R]
    
    # fifo_operations are the commands that task manager should complete
    fifo_operations = fifo_operations[fifo_R:]

    # Adding New Tasks into the Task Manager
    for num in range(1, fifo_T+1):
        runFifo.newTask(num)

    # Setting Task Manager's current resource and total recource to fifo_unit
    runFifo.currentResource = fifo_unit
    runFifo.totalResource = fifo_unit

    # Until all of the tasks are completed, add the input commands (activities) into task manager
    while len(fifo_operations) > 0:
        runFifo.newActivity(*fifo_operations[:4])
        fifo_operations = fifo_operations[4:]
    
    # Run Task Manager using fifo
    runFifo.start()
    
    # Run Banker
    runBanker = TaskList('Banker')

    # Error Message if wrong file name or if file does not exist
    if not os.path.isfile(inputFile):
        print("Input file does not exist. Please Restart.")
        return

    # Receieve and organize Input File
    with open(inputFile, "r") as File:
        banker_operations = []
        for line in File:
            banker_operations += [int(element) if element.isnumeric() else element for element in line.strip().split()]
    
    # banker_T is the number of tasks
    banker_T = banker_operations.pop(0)

    # banker_R is the number of resource types
    banker_R = banker_operations.pop(0)
    runBanker.resource = banker_R
    
    # Number of units presents of each resource type 
    banker_unit = banker_operations[:banker_R]

    # fifo_operations are the commands that task manager should complete
    banker_operations = banker_operations[banker_R:]

    # Adding New Tasks into the Task Manager
    for num in range(1, banker_T+1):
        runBanker.newTask(num)

    # Setting Task Manager's current resource and total recource to banker_unit
    runBanker.currentResource = banker_unit
    runBanker.totalResource = banker_unit

    # Until all of the tasks are completed, add the input commands (activities) into task manager
    while len(banker_operations) > 0:
        runBanker.newActivity(*banker_operations[:4])
        banker_operations = banker_operations[4:]

    # Run Task Manager using Banker Algo
    runBanker.start()


if __name__ == "__main__":
    # Run Program
    main()

