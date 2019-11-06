import os

'''
Class Activity is a representation of an activity that a 
task should complete
'''

class Activity():
    def __init__(self, *args):
        self.status = args[0]               # Activity Status: initiate, request, compute, relase, and terminate
        
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
    def __init__(self,*args):
        # > Task Attributes
        self.state = "unstarted"            # Task can be: unstarted, running, blocked, terminated, or aborted
        self.taskNum = args[0]              # Task Number
        self.initialClaim = [0] * args[-1]  # Initial claim of resource
        self.holding = [0] * args[-1]       # Resources held by task

        # > Time attributes
        self.currentCycle = 0               # Time / Cycles taken to run current task
        self.remainingCycle = 0             # Time / Cycles remaining during computing
        self.waitTime = 0                   # Time / Cycles a task waited
        self.blockedCycle = -1              # Time / Cycle when task was blocked

        self.execution = []                 # List of activities to execute (in order)

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
    def block(self, activity = None, deadlocked = False):
        if activity is not None:
            self.execution.inset(0, activity)       # need to be constnatly in front of execution list
        if deadlocked == False:
            self.state = "blocked"
            if self.blockedCycle < 0:
                self.blockedCycle = self.currentCycle
            self.waitTime +=1
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
    def updateHoldResource(self, resourceType, value = -1):
        if value >= 0 and value <= self.getClaim(resourceType):
            self.holding[resourceType -1] = value
        return self.holding[resourceType -1]

'''
Class TaskList is the list of all tasks that needs to be exectued
using resource allocation algorithms (FIFO / Banker)
'''

class TaskList(list):
    def __inint__(self, allocType):
        super(TaskList, self).__init__()
        self.resource = 0                       # Total number of resource Type (careful of name)
        self.currentResource = []                   # List of current resources
        self.totalResource = []                     # List of total amount of resources

        # If statement for choosing allocation type
        if allocType == "FIFO":
            self.allocType = FIFO()                 # Running FIFO by creating FIFO instance
        elif allocType == "Banker":
            self.allocType = Banker()               # Running Banker by creating Banker instance
        
        # Starting Resource Allocation
        def start(self):
            self.allocType.run(self)
        
        ''' > Functions Managing Activity'''

        # New activities added depending on input parameter (task number)
        def newActivity(self, *specs):
            activity = Activity(*specs)
            task = self[activity.taskNum_ - 1]
            task.newActivity(activity)

        ''' > Functions Managing Tasks'''
        
        # New tasks created with input parameter & appended to taskList
        def newTask(self, *specs):
            self.append(Task(*specs, self.resource))
        
        # Retrieving tasks in particular state
        def taskByState(self, tState):
            tasks = []
            for task in self:
                if task.state == tState:
                    tasks.append(task)
            return tasks

        ''' > Functions Managing Resources'''
        # Getting held resources and updating value of held resource
        def updateHoldResource(self, resourceType, value = -1):
            if value >= 0:
                self.holding[resourceType -1] = value
            return self.holding[resourceType -1]

        # Responds to task request through resource allocation
        def allocate(self, task, resourceType, value):
            # Updating Task Resource
            taskResource = task.updateHoldResource(resourceType)
            task.updateHoldResource(resourceType, taskResource+ value)
            
            # Update TaskList
            heldResource = self.updateHoldResource(resourceType)
            self.updateHoldResource(resourceType, heldResource - value)
        
        # Release resource when told to release
        def release(self, task, resourceType = None, value = None):
            if resourceType is not None and value is not None:
                # Updating Task Resource
                taskResource = task.updateHoldResource(resourceType)
                task.updateHoldResource(resourceType, taskResource - value)
                
                # Update TaskList
                heldResource = self.updateHoldResource(resourceType)
                self.updateHoldResource(resourceType, heldResource + value)
            else:
                # To release all of the resource
                for i in range(1, 1+self.resouce):
                    self.updateHoldResource(i, self.updateHoldResource(i) + task.updateHoldResource(i))


        ''' > Checker Functions'''

        # Boolean that checks whether resouce can be allocated
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
            for i in range(1,self.resourceType+1):
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
                bt.block(activity, deadlocked= True)
                if self.bool_allocate(activity.resourceType, activity.claim):
                    return False
            
            return True


# class FIFO():
    
# class Banker():