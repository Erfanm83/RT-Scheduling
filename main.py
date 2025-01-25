import threading
import time
import os
import json
from subsystem1 import handle_subSystem1
from subsystem2 import handle_subSystem2
from subsystem3 import handle_subSystem3
from subsystem4 import handle_subSystem4

# Shared resource pool
resource_pool = {}
allsubSystemResources = []
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
    initialize_resource_pool()
    check_valid_input(allsubSystemTasks, allsubSystemResources)
    
    # Creating subsystem handler threads
    thread1 = threading.Thread(target=handle_subSystem1, args=(allsubSystemResources[0], allsubSystemTasks[0]))
    thread2 = threading.Thread(target=handle_subSystem2, args=(allsubSystemResources[1], allsubSystemTasks[1]))
    thread3 = threading.Thread(target=handle_subSystem3, args=(allsubSystemResources[2], allsubSystemTasks[2]))
    thread4 = threading.Thread(target=handle_subSystem4, args=(allsubSystemResources[3], allsubSystemTasks[3]))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # Wait for all threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    print("All threads have finished execution.")

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
    global allsubSystemResources, allsubSystemTasks

    with open("./in.txt", 'r') as file:
        # Read subsystem resources
        for _ in range(4):
            line = file.readline().strip()
            resources = list(map(int, line.split()))
            allsubSystemResources.append(resources)

        # Read subsystem tasks
        for _ in range(4):
            subSystemTask = []
            while True:
                line = file.readline().strip()
                if line == "$":
                    break
                subSystemTask.append(line)
            allsubSystemTasks.append(subSystemTask)

def initialize_resource_pool():
    """Initialize the global resource pool from the parsed subsystem resources"""
    global resource_pool
    for i, resources in enumerate(allsubSystemResources):
        subsystem_name = f'sub{i + 1}'
        resource_pool[subsystem_name] = {
            'r1': resources[0],
            'r2': resources[1],
            'lock': threading.Lock()
        }

def take_resources(requesting_subsystem, r1_needed, r2_needed):
    """
    Borrow resources from other subsystems.
    Returns the amounts borrowed for r1 and r2.
    """
    global resource_pool
    borrowed_r1 = 0
    borrowed_r2 = 0

    for subsystem, data in resource_pool.items():
        if subsystem == requesting_subsystem:
            continue  # Skip the requesting subsystem itself

        with data['lock']:
            # Check and take available resources
            if r1_needed > 0 and data['r1'] > 0:
                borrow_r1 = min(r1_needed, data['r1'])
                data['r1'] -= borrow_r1
                borrowed_r1 += borrow_r1
                r1_needed -= borrow_r1
            
            if r2_needed > 0 and data['r2'] > 0:
                borrow_r2 = min(r2_needed, data['r2'])
                data['r2'] -= borrow_r2
                borrowed_r2 += borrow_r2
                r2_needed -= borrow_r2

            if r1_needed <= 0 and r2_needed <= 0:
                break  # Stop if we've borrowed enough

    return borrowed_r1, borrowed_r2

def return_resources(requesting_subsystem, r1_returned, r2_returned):
    """
    Return borrowed resources to their original subsystems.
    """
    global resource_pool
    # In this simple example, we'll distribute the returned resources back equally among all other subsystems.
    for subsystem, data in resource_pool.items():
        if subsystem == requesting_subsystem:
            continue

        with data['lock']:
            data['r1'] += r1_returned
            data['r2'] += r2_returned
            r1_returned = 0
            r2_returned = 0

        if r1_returned <= 0 and r2_returned <= 0:
            break

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
