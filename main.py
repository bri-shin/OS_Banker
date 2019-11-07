import task
from task import TaskList
import sys
import os

'''
Main function - running the resource allocators (FIFO and Banker)
'''


def main():
    if len(sys.argv[1]) < 1:
        print("Input file is required")

    inputFile = sys.argv[1]

    # Running FIFO

    runFifo = TaskList('FIFO')
    print("This is the type:", type(runFifo))
    if not os.path.isfile(inputFile):
        print("Input file does not exist. Please Restart.")
        return

    with open(inputFile, "r") as File:
        operations = []
        for line in File:
            # for element in line.strip().split():
            #     if element.isnumeric():
            #         operations.append(int(element))
            operations += [int(element) if element.isnumeric()
                           else element for element in line.strip().split()]

    T = operations.pop(0)
    R = operations.pop(0)
    runFifo.resource = R
    unit = operations[:R]
    tokens = operations[R:]

    for num in range(1, T+1):
        runFifo.newTask(num)
    runFifo.currentResource = unit
    runFifo.totalResource = unit

    while len(operations) > 0:
        runFifo.newActivity(*operations[:5])
        operations = operations[5:]

    runFifo.start()

    # Run Banker

    runBanker = TaskList('Banker')

    if not os.path.isfile(inputFile):
        print("Input file does not exist. Please Restart.")
        return

    with open(inputFile, "r") as File:
        operations = []
        for line in File:
            # for element in line.strip().split():
            #     if element.isnumeric():
            #         operations.append(int(element))
            operations += [int(element) if element.isnumeric()
                           else element for element in line.strip().split()]

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
