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

    ''' > Functions for Managing Activities'''

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

