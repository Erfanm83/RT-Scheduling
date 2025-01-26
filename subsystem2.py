import threading
import time
import os
import json
from resource_utils import take_resources, return_resources

core1_ready_queue = "./ready_queues/core1_ready_queue2.json"
core2_ready_queue = "./ready_queues/core2_ready_queue2.json"
job_list_file = "./ready_queues/job_list.json"

# Mutex locks
job_list_lock = threading.Lock()
print_snapshot_lock = threading.Lock()

class Job:
    def __init__(self, id, name, burst_time, resource1, resource2, arrival_time, **kwargs):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.remain_time = kwargs.get("remain_time", burst_time)
        self.state = kwargs.get("state", "Ready")  # Default state
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
                'state': obj.state
            }
        return super().default(obj)

def handle_subSystem2(tasks, y):
    """
        Handles SubSystem2 that has a ready queues and NO wait queue.

        Simulates each CPU core with a thread(here two cores available).
    """
    # Initialize queue
    core_queue = []

    for t in tasks:
        core_queue.append(t.split(' '))
    
    # Create JobLists for each core
    JobList = create_job_list(core_queue)

    # Write initial job lists to files
    write_job_list(JobList)

    # Initialize and start core thread
    thread = threading.Thread(target=handle_core)
    thread.start()

def Shortest_Remaining_Time_First(tasks):
    # Parse tasks into a list of dictionaries
    parsed_tasks = []
    for task in tasks:
        id = task.id
        name = task.name
        burst_time = int(task.burst_time)
        resource1 = int(task.resource1)
        resource2 = int(task.resource2)
        arrival_time = int(task.arrival_time)
        parsed_tasks.append(Job(id, name, burst_time, resource1, resource2, arrival_time))
    
    time = 0
    schedule = []
    while parsed_tasks:
        # Filter tasks that have arrived
        available_tasks = [task for task in parsed_tasks if task.arrival_time <= time]
        if not available_tasks:
            time += 1
            continue

        # Sort by remaining time
        available_tasks.sort(key=lambda x: x.remain_time)

        # Select the task with the shortest remaining time
        current_task = available_tasks[0]
        start_time = time
        if current_task.remain_time > 0:
            current_task.remain_time -= 1
            time += 1

        schedule.append(f"{current_task.id} {time - start_time}")

        # If the task is completed, remove it from the list
        if current_task.remain_time == 0:
            parsed_tasks.remove(current_task)

    # Combine consecutive tasks
    combined_schedule = []
    current_task = None
    current_duration = 0

    for entry in schedule:
        task, duration = entry.split()
        duration = int(duration)
        if current_task is None:
            current_task = task
            current_duration = duration
        elif task == current_task:
            current_duration += duration
        else:
            combined_schedule.append((int(current_task), current_duration))
            current_task = task
            current_duration = duration

    if current_task is not None:
        combined_schedule.append((int(current_task), current_duration))
    return combined_schedule

def create_job_list(core_queue):
    job_list = []
    job_id = 0
    for item in core_queue:
        if item:
            job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4])))
            job_id += 1
    return job_list

def handle_core():
    '''
    Handles tasks for a specific core.
    '''
    # Read the job list for the core
    JobList = read_job_list()

    # Scheduling using shortest remaining time first for each core
    srtfList = Shortest_Remaining_Time_First(JobList)  # Shortest Remaining Time First
    print("schedule: ", srtfList)

    current_time = 0
    core1_queue = []
    core2_queue = []
    while not len(srtfList) == 0:
        # Pop the next item in order
        if(srtfList):
            job_to_process = srtfList.pop(0)
            print("popped item (ordered): ", job_to_process)

        process_id = job_to_process[0]
        print("process_id : " , process_id)

        if process_id < len(JobList) and JobList[process_id] is not None:
            job_to_process = JobList[process_id]

        if not len(core1_queue) == 0 and len(core2_queue) == 0:
            print("cores are empty and no jobs left in cores, exiting...")
            # terminate_threads(threads, stop_event2)
            break

        # deadlock_job_id = detect_deadlock(job_list_subsystem2)
        # if deadlock_job_id is not None:
        #     resolve_deadlock(job_list_subsystem2, deadlock_job_id)

        r1, r2 = take_resources("sub2", job_to_process.resource1, job_to_process.resource2)
        resources = [r1, r2]
        # Handle resource checks and execution
        if check_resource(resources, job_to_process):
            # resources[0] -= job_to_process.resource1
            # resources[1] -= job_to_process.resource2
            job_to_process.state = "Running"
            print(f"Job {job_to_process.name} is running r1:{resources[0]} and r2:{resources[1]}")
            return_resources("sub2", r1, r2)
            execute_task(resources, job_to_process)
        else:
            print(f"we don't have resource for {job_to_process.name}")
            # Add job_to_process to the head of srtfList
            srtfList.insert(0, job_to_process)
            job_to_process.state = "Waiting"
            print(f"Job {job_to_process.name} is waiting for resources.")
        write_job_list(srtfList)

        # Call print_snapshot at the end of each iteration
        print_snapshot(current_time, resources, core1_queue, core2_queue)
        current_time += 1

def detect_deadlock(job_list):
    # Simple deadlock detection by checking for circular wait
    resource_allocation = {job.id: (job.resource1, job.resource2) for job in job_list}
    resource_request = {job.id: (job.resource1, job.resource2) for job in job_list if job.state == "Waiting"}

    for job_id, resources in resource_request.items():
        if resources in resource_allocation.values():
            return job_id  # Deadlock detected, return the job id involved in deadlock
    return None

def resolve_deadlock(job_list, job_id):
    # Preempt the job involved in deadlock
    for job in job_list:
        if job.id == job_id:
            job.state = "Ready"
            job.remain_time = job.burst_time  # Reset remaining time
            print(f"Deadlock resolved by preempting job {job.id}")
            break

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

def print_snapshot(curr_time, resources, core1_queue, core2_queue):
    """
    Print the current state of subsystem2 to the out.txt file.
    Format:
    Time = <curr_time>
    Sub2:
        Resources: R1: <r1> R2: <r2>
        Core1:
            Running Task: <task>
            Ready Queue: [<ready tasks>]
        Core2:
            Running Task: <task>
            Ready Queue: [<ready tasks>]
    """
    # Generate the formatted snapshot string
    snapshot_lines = [f"Time = {curr_time}\n", "\nSub2:\n"]
    snapshot_lines.append(f"\tResources: R1: {resources[0]} R2: {resources[1]}\n")
    
    # For core1
    running_task1 = core1_queue[0].name if core1_queue else "None"
    ready_queue1 = [job.name for job in core1_queue[1:]]
    snapshot_lines.append("\tCore1:\n")
    snapshot_lines.append(f"\t\tRunning Task: {running_task1}\n")
    snapshot_lines.append(f"\t\tReady Queue: {ready_queue1}\n")
    
    # For core2
    running_task2 = core2_queue[0].name if core2_queue else "None"
    ready_queue2 = [job.name for job in core2_queue[1:]]
    snapshot_lines.append("\tCore2:\n")
    snapshot_lines.append(f"\t\tRunning Task: {running_task2}\n")
    snapshot_lines.append(f"\t\tReady Queue: {ready_queue2}\n")
    
    snapshot_lines.append("\n---------------------------------------------------------------------\n")
    
    # Attempt to write the snapshot to out.txt using a global lock
    with print_snapshot_lock:
        with open("out.txt", "a") as out_file:
            out_file.writelines(snapshot_lines)
