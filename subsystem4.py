import threading
import time
import os
import json
import random

wait_queue_file = "./wait_queues/wait_queue4.json"
core1_queue_file = "./ready_queues/core1_ready_queue4.json"
core2_queue_file = "./ready_queues/core2_ready_queue4.json"
job_list_file = "./ready_queues/ready_queue4.json"

# Mutex locks
job_list_lock = threading.Lock()

class Job:
    def __init__(self, id, name, burst_time, resource1, resource2, arrival_time, dependencies=None, **kwargs):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.remain_time = kwargs.get("remain_time", burst_time)
        self.state = kwargs.get("state", "Ready")  # Default state
        self.dependencies = dependencies if dependencies else []
        self.lock = threading.Lock()
    def __str__(self):
        return f""" Job properties:
        {"id":^10} | {"name":^10} | {"burst time":^10} | {"resource1":^10} | {"resource2":^10} | {"arrival time":^12} | {"state":^10} |
        {self.id:^10} | {self.name:^10} | {self.burst_time:^10} | {self.resource1:^10} | {self.resource2:^10} | {self.arrival_time:^12} | {self.state:^10} |"""

class JobEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Job):
            return {
                'id': obj.id,
                'name': obj.name,
                'burst_time': obj.burst_time,
                'resource1': obj.resource1,
                'resource2': obj.resource2,
                'arrival_time': obj.arrival_time,
                'remain_time': obj.remain_time,
                'state': obj.state,
                'dependencies': obj.dependencies
            }
        return super().default(obj)

def handle_subSystem4(resources, tasks):
    """
        Handles SubSystem4 that has 2 cores and uses FCFS scheduling.
        Tasks may have dependencies and a 30% chance of re-execution upon failure.
    """
    # Initialize queue
    core_queue = []

    for t in tasks:
        core_queue.append(t.split(' '))
    
    # Create JobLists for each core
    JobList = create_job_list(core_queue)

    # Write initial job lists to files
    write_job_list(JobList)

    # Create stop event for threads
    stop_event = threading.Event()

    # Initialize and start core threads
    threads = []
    for i in range(2):
        thread = threading.Thread(target=handle_core, args=(resources, stop_event, i+1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def create_job_list(core_queue):
    job_list = []
    job_id = 0
    for item in core_queue:
        if item:
            dependencies = item[6].split(',') if len(item) > 6 else []
            job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4]), dependencies))
            job_id += 1
    return job_list

def handle_core(resources, stop_event, core_id):
    '''
    Handles tasks for a specific core.
    '''
    current_time = 0

    # Read the job list for the core
    JobList = read_job_list()

    # Scheduling using FCFS for each core
    fcfsList = sorted(JobList, key=lambda x: x.arrival_time)
    print(f"Core {core_id} schedule: ", fcfsList)

    while fcfsList:
        # Pop the next item in order
        job_to_process = fcfsList.pop(0)
        print(f"Core {core_id} popped item (ordered): ", job_to_process)

        if job_to_process.dependencies:
            # Check if dependencies are met
            dependencies_met = all(dep.state == "Completed" for dep in JobList if dep.id in job_to_process.dependencies)
            if not dependencies_met:
                print(f"Core {core_id} waiting for dependencies of job {job_to_process.name}")
                fcfsList.append(job_to_process)
                continue

        if check_resource(resources, job_to_process):
            resources[0] -= job_to_process.resource1
            resources[1] -= job_to_process.resource2
            job_to_process.state = "Running"
            print(f"Core {core_id} Job {job_to_process.name} is running r1:{resources[0]} and r2:{resources[1]}")
            execute_task(resources, job_to_process)
            if random.random() < 0.3:  # 30% chance of re-execution
                print(f"Core {core_id} Job {job_to_process.name} failed, re-executing")
                job_to_process.state = "Ready"
                fcfsList.append(job_to_process)
            else:
                job_to_process.state = "Completed"
        else:
            print(f"Core {core_id} we don't have resource for {job_to_process.name}")
            fcfsList.append(job_to_process)
            job_to_process.state = "Waiting"

        write_job_list(fcfsList)

        current_time += 1

def write_job_list(job_list):
    """Write job list to JSON file with proper synchronization"""
    with job_list_lock:
        try:
            # Convert job list to JSON serializable format
            job_data = [json.loads(json.dumps(job, cls=JobEncoder)) for job in job_list]
            
            # Write to file
            with open(job_list_file, 'w') as file:
                json.dump(job_data, file, indent=4)
        except Exception as e:
            print(f"Error: {str(e)}")

def read_job_list():
    """Read job list from JSON file with proper synchronization"""
    with job_list_lock:
        try:
            # Attempt to open and read the job list file
            with open(job_list_file, 'r') as file:
                job_data = json.load(file)

            # Convert JSON objects back into Job instances
            job_list = [Job(**job) for job in job_data]
            return job_list
        except FileNotFoundError:
            print("Error: Job list file not found.")
            return []  # Return an empty list if the file is not found
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON from job list file.")
            return []  # Return an empty list if there is a decoding error
        except Exception as e:
            print(f"Error: {str(e)}")
            return []  # Return an empty list if any other exception occurs

def check_resource(resources, job_to_process):
    '''
    check whether resources can meet the needs of task or not

    if YES, put them to cores and execute the task

    '''
    if 0 <= resources[0] - job_to_process.resource1 and 0 <= resources[1] - job_to_process.resource2:
        return True
    else:
        return False

def execute_task(resources, job_to_process):
    '''
    execute task on core and print snapShot of system

    print_snapshot()
    '''
    resources[0] += job_to_process.resource1
    resources[1] += job_to_process.resource2

def terminate_threads(threads, stop_event):
    stop_event.set()
    for thread in threads:
        thread.join()