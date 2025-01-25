import threading
import time
import os
import json
from subsystem1 import handle_subSystem1
from subsystem2 import handle_subSystem2
from subsystem3 import handle_subSystem3
from subsystem4 import handle_subSystem4
from resource_utils import initialize_resource_pool_from_file

# Shared resource pool
resource_pool = {}
allsubSystemTasks = []

# Mutex locks
wait_queue_lock = threading.Lock()
job_list_lock = threading.Lock()

def main():
    read_data_from_file()
    initialize_resource_pool_from_file("in.txt")
    
    # Creating subsystem handler threads
    thread1 = threading.Thread(target=handle_subSystem1, args=(allsubSystemTasks[0], []))
    thread2 = threading.Thread(target=handle_subSystem2, args=(allsubSystemTasks[1], []))
    thread3 = threading.Thread(target=handle_subSystem3, args=(allsubSystemTasks[2], []))
    thread4 = threading.Thread(target=handle_subSystem4, args=(allsubSystemTasks[3], []))

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

def read_data_from_file():
    global allsubSystemTasks

    with open("./in.txt", 'r') as file:
        # Read subsystem resources
        for _ in range(4):
            line = file.readline().strip()

        # Read subsystem tasks
        for _ in range(4):
            subSystemTask = []
            while True:
                line = file.readline().strip()
                if line == "$":
                    break
                subSystemTask.append(line)
            allsubSystemTasks.append(subSystemTask)

if __name__ == "__main__":
    main()
