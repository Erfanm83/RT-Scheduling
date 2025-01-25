import threading
import time
import os
import json
from subsystem1 import handle_subSystem1
from subsystem2 import handle_subSystem2
from subsystem3 import handle_subSystem3
from subsystem4 import handle_subSystem4

allsubSystemResourses = []
allsubSystemTasks = []

# Mutex locks
wait_queue_lock = threading.Lock()
job_list_lock = threading.Lock()

# File paths
wait_queue_file = "wait_queue.json"
job_list_file = "job_list.json"

def main():
    initialize_json_files()
    read_data_from_file()
    check_valid_input(allsubSystemTasks , allsubSystemResourses)
    
    # Creating subsystem handler threads
    # thread1 = threading.Thread(target= handle_subSystem1, args=(allsubSystemResourses[0], allsubSystemTasks[0])).start()
    # thread2 = threading.Thread(target= handle_subSystem2, args=(allsubSystemResourses[1], allsubSystemTasks[1])).start()
    # thread3 = threading.Thread(target= handle_subSystem3, args=(allsubSystemResourses[2], allsubSystemTasks[2])).start()
    thread4 = threading.Thread(target= handle_subSystem4, args=(allsubSystemResourses[3], allsubSystemTasks[3])).start()

    # Wait for all threads to complete
    # thread1.join()
    # thread2.join()
    # thread3.join()
    # thread4.join()

    # print("All threads have finished execution.")

def initialize_json_files():
    """Initialize JSON files with empty data if they don't exist"""
    default_data = {'jobList1': [], 'jobList2': [], 'jobList3': []}
    
    # Initialize job_list_file
    if not os.path.exists(job_list_file):
        with open(job_list_file, 'w') as f:
            json.dump(default_data, f)
    
    # Initialize wait_queue_file
    if not os.path.exists(wait_queue_file):
        with open(wait_queue_file, 'w') as f:
            json.dump([], f)

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


    def default(self, obj):
        if isinstance(obj, Job):
            return {
                'id': obj.id,
                'name': obj.name,
                'burst_time': obj.burst_time,
                'resource1': obj.resource1,
                'resource2': obj.resource2,
                'arrival_time': obj.arrival_time,
                'CPU_dest': obj.CPU_dest,
                'remain_time': obj.remain_time,
                'wait_time': obj.wait_time,
                'arrival_wait_time': obj.arrival_wait_time,
                'priority': obj.priority,
                'quantum': obj.quantum,
                'state': obj.state
            }
        return super().default(obj)

def check_valid_input(allsubSystemTasks , allsubSystemResources):
    subsystemIndex = 1
    for subsystemTask in allsubSystemTasks:
        if subsystemIndex == 3:
            sumr1 = sum(resource[0] for resource in allsubSystemResources)
            sumr2 = sum(resource[1] for resource in allsubSystemResources)
            for t in subsystemTask:
                taskList = t.split(' ')
                r1 = int(taskList[2])
                r2 = int(taskList[3])
                if r1 > sumr1 or r2 > sumr2:
                    print(f"""
                    Error: Task requires more resources than available.
                    In Subsystem {subsystemIndex} 
                    {t[0:3]} Requested: r1: {r1} and r2: {r2}
                    Available Resources are r1: {sumr1} and r2: {sumr2}.
                    Exiting from program........
                    Try again later.
                    """)
                    exit(1)
        else:    
            for t in subsystemTask:
                taskList = t.split(' ')
                r1 = int(taskList[2])
                r2 = int(taskList[3])
                availableR1 = allsubSystemResources[subsystemIndex - 1][0]
                availableR2 = allsubSystemResources[subsystemIndex - 1][1]
                if r1 > availableR1 or r2 > availableR2:
                    print(f"""
                    Error: Task requires more resources than available.
                    In Subsystem {subsystemIndex} 
                    {t[0:3]} Requested: r1: {r1} and r2: {r2}
                    Available Resources are r1: {availableR1} and r2: {availableR2}.
                    Exiting from program........
                    Try again later.
                    """)
                    exit(1)
        subsystemIndex += 1

if __name__ == "__main__":
    main()
