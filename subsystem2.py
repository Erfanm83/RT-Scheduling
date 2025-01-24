import threading
import time
import os
import json

wait_queue_file = "sub2_wait_queue.json"
job_list_file = "sub2_job_list.json"

# Mutex locks
wait_queue_lock = threading.Lock()
job_list_lock = threading.Lock()

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

def core_execution(core_id, job_list, resources, condition):
    while job_list:
        with condition:
            job_list.sort(key=lambda x: x.remain_time)  # Shortest Remaining Time First
            for job in job_list:
                if job.state == "Ready":
                    job.state = "Running"
                    with job.lock:
                        print(f"Core {core_id} is executing job {job.id}")
                        # Simulate job execution
                        job.remain_time = 0
                        job.state = "Completed"
                        print(f"Core {core_id} completed job {job.id}")
                    break
            condition.notify_all()
            condition.wait()  # Wait for the next job to be ready

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

        schedule.append(f"{current_task.name} {time - start_time}")

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
            combined_schedule.append((current_task, current_duration))
            current_task = task
            current_duration = duration

    if current_task is not None:
        combined_schedule.append((current_task, current_duration))
    return combined_schedule

def handle_subSystem2(resources, tasks):
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
    write_job_list("jobList", JobList)

    # Create stop event for threads
    stop_event = threading.Event()

    # Initialize and start core thread
    thread = threading.Thread(target=handle_core, args=("jobList", resources, stop_event))
    thread.start()

    # Main loop to manage the wait queue
    curr_time = 0
    while True:
        # Dynamically read the job lists to get their current state
        JobList = receive_jobList("jobList")

        # Exit condition: wait queue is empty and no jobs left in cores
        if len(JobList) == 0:
            stop_event.set()
            thread.join()
            print("Wait queue is empty and no jobs left in cores, exiting...")
            break

        curr_time += 1

def create_job_list(core_queue):
    job_list = []
    job_id = 0
    for item in core_queue:
        if item:
            job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4])))
            job_id += 1
    return job_list

def write_job_list(core_name, job_list):
    """Write job list to JSON file with proper synchronization"""
    with job_list_lock:
        try:
            # Read existing data
            try:
                with open(job_list_file, 'r') as file:
                    job_lists = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                job_lists = {'jobList': []}
            
            # Update the specific core's job list
            job_lists[core_name] = [json.loads(json.dumps(job, cls=JobEncoder)) for job in job_list]
            
            # Write back to file
            with open(job_list_file, 'w') as file:
                json.dump(job_lists, file, indent = 4)
        except Exception as e:
            print(f"Error writing to {core_name}: {str(e)}")

def initialize_cores_and_threads(resources, job_lists, stop_event):
    threads = []
    for i, job_list in enumerate(job_lists, start=1):
        thread = threading.Thread(target=handle_core, args=(f"jobList{i}", resources, stop_event))
        threads.append(thread)
        thread.start()
    return threads

def handle_core(core_name, resources, stop_event):
    '''
    Handles tasks for a specific core.
    '''
    current_time = 0
    # Read the job list for the core
    JobList = receive_jobList(core_name)

    # Scheduling using shortest remaining time first for each core
    schedule = Shortest_Remaining_Time_First(JobList)  # Shortest Remaining Time First
    print("schedule: ", schedule)

    while not len(JobList) == 0 or not stop_event.is_set():
        # Pop the next item in order
        if(JobList):
            job_to_process = JobList.pop(0)
            print("popped item (ordered): ", job_to_process)

        process_id = job_to_process.id
        print("process_id : " , process_id)

        # deadlock_job_id = detect_deadlock(job_list_subsystem2)
        # if deadlock_job_id is not None:
        #     resolve_deadlock(job_list_subsystem2, deadlock_job_id)

        # Process the job without fully removing it from JobList
        # if process_id < len(JobList) and JobList[process_id] is not None:
        #     job_to_process = JobList[process_id]

        # Handle resource checks and execution
        if check_resource(resources, job_to_process):
            print(f"we have resource for {job_to_process.name}")
            # resources[0] -= job_to_process.resource1
            # resources[1] -= job_to_process.resource2
            # job_to_process.state = "Running"
            # print(f"Job {job_to_process.name} is running r1:{resources[0]} and r2:{resources[1]}")
            # # job_to_process.burst_time = job_to_process.burst_time - job_to_process.quantum
            # execute_task(core_name, resources, job_to_process)
        else:
            print(f"we don't have resource for {job_to_process.name}")
            # job_to_process.state = "Waiting"
            # print(f"Job {job_to_process.name} is waiting for resources.")
            # # Write to a txt file when a process enters the wait queue
            # with open("wait_queue_log.txt", "a") as log_file:
            #     log_file.write(f"Time {current_time}: Job {job_to_process.name} waits for resource\n")

        # Write updated job list and wait queue back to the file
        # write_job_list(core_name, JobList)

        # current_time += 1

def receive_jobList(core_name):
    """Read job list from JSON file with proper synchronization"""
    with job_list_lock:
        try:
            with open(job_list_file, 'r') as file:
                content = file.read().strip()
                if not content:
                    return []
                job_lists = json.loads(content)
                job_data = job_lists.pop(core_name, [])

                # Write back the updated job lists without the read core_name
                with open(job_list_file, 'w') as file:
                    json.dump(job_lists, file, indent=4)

                # Ensure only valid mappings are passed to Job
                if not all(isinstance(job, dict) for job in job_data):
                    print(f"Warning: Invalid job data format for {core_name}: {job_data}")
                    job_data = [job for job in job_data if isinstance(job, dict)]

                return [Job(**job) for job in job_data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading job list file: {e}")
            return []
        
def write_wait_queue(wait_queue):
    '''
    Writes the wait queue to a file, ensuring mutual exclusion.
    '''
    with wait_queue_lock:
        with open(wait_queue_file, 'w') as file:
            json.dump([job.__dict__ for job in wait_queue], file)  # Convert Job objects to dicts
        print(f"Wait queue written to {wait_queue_file}: {[job.name for job in wait_queue]}")

def check_resource(resources, job_to_process):
    '''
    check whether resources can meet the needs of task or not

    if YES, put them to cores and execute the task

    if NO, put them to wait queue

    '''
    if 0 <= resources[0] - job_to_process.resource1 and 0 <= resources[1] - job_to_process.resource2:
        return True
    else:
        return False

def execute_task(core_name, resources, job_to_process):
    '''
    execute task on core and print snapShot of system

    print_snapshot()
    '''
    resources[0] += job_to_process.resource1
    resources[1] += job_to_process.resource2
