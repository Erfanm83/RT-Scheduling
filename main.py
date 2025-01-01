import threading
import time

allsubSystemResourses = []
allsubSystemTasks = []

def main():
    print("Subsystem Resources:")
    read_data_from_file()
    for res in allsubSystemResourses:
        print(res)
    
    print("\nSubsystem Tasks:")
    for idx, tasks in enumerate(allsubSystemTasks):
        print(f"Subsystem {idx + 1} Tasks:")
        for task in tasks:
            print(f"  {task}")

    # Creating subsystem handler threads
    thread1 = threading.Thread(target= handle_subSystem1).start()
    # near future...
    thread2 = threading.Thread(target= handle_subSystem2).start()
    thread3 = threading.Thread(target= handle_subSystem3).start()
    thread4 = threading.Thread(target= handle_subSystem4).start()

    # Wait for all threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    print("All threads have finished execution.")

def read_data_from_file():
    global allsubSystemResourses, allsubSystemTasks

    with open("./in.txt", 'r') as file:
        # Read subsystem resources
        for _ in range(4):
            line = file.readline().strip()
            resources = list(map(int, line.split()))
            allsubSystemResourses.append(resources)

        # Read subsystem tasks
        for _ in range(4):
            subSystemTask = []
            while True:
                line = file.readline().strip()
                if line == "$":
                    break
                subSystemTask.append(line)
            allsubSystemTasks.append(subSystemTask)

def handle_subSystem1():
    wait_queue = list()
    ready_queue = list()
    
    thread1 = threading.Thread(target=handle_subSystem1, args=(allsubSystemResourses[0], allsubSystemTasks[0]))
    # near future
    thread2 = threading.Thread(target=handle_subSystem2, args=(allsubSystemResourses[1], allsubSystemTasks[1]))
    thread3 = threading.Thread(target=handle_subSystem3, args=(allsubSystemResourses[2], allsubSystemTasks[2]))
    thread4 = threading.Thread(target=handle_subSystem4, args=(allsubSystemResourses[3], allsubSystemTasks[3]))

    # Wait for all threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()


# near future...
def handle_subSystem1(resources, tasks):
    wait_queue = list()
    ready_queue = list()


def handle_subSystem2(resources, tasks):
   pass

def handle_subSystem3(resources, tasks):
    pass

def handle_subSystem4(resources, tasks):
    pass

if __name__ == "__main__":
    main()

