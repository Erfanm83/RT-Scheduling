import threading
import time
import os
import json

wait_queue_file = "wait_queue.json"
job_list_file = "job_list.json"

# Mutex locks
wait_queue_lock = threading.Lock()
job_list_lock = threading.Lock()

class Job:
    def __init__(self, id ,name, burst_time, resource1, resource2, arrival_time, CPU_dest, **kwargs):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.CPU_dest = CPU_dest
        self.remain_time = kwargs.get("remain_time", burst_time)
        self.wait_time = kwargs.get("wait_time", 0)
        self.arrival_wait_time = kwargs.get("arrival_wait_time", 0)
        self.priority = kwargs.get("priority", 0)
        self.quantum = kwargs.get("quantum", 0)
        self.state = kwargs.get("state", "Ready")  # Default state
    def __str__(self):
        return f""" Job properties:
        {"id":^10} | {"name":^10} | {"burst time":^10} | {"resource1":^10} | {"resource2":^10} | {"arrival time":^12} | {"CPU Dest":^10} | {"priority":^10} | {"quantum":^10} | {"state":^10} |
        {self.id:^10} | {self.name:^10} | {self.burst_time:^10} | {self.resource1:^10} | {self.resource2:^10} | {self.arrival_time:^12} | {self.CPU_dest:^10} | {self.priority:^10} | {self.quantum:^10} | {self.state:^10} |"""

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
                'CPU_dest': obj.CPU_dest,
                'remain_time': obj.remain_time,
                'wait_time': obj.wait_time,
                'arrival_wait_time': obj.arrival_wait_time,
                'priority': obj.priority,
                'quantum': obj.quantum,
                'state': obj.state
            }
        return super().default(obj)

def handle_subSystem1(resources, tasks):
    """
        Handles SubSystem1 that has 3 ready queues and 1 wait queue.

        Simulates each CPU core with a thread and the main thread manages the wait queue.
    """
    # Initialize queues
    core1_queue, core2_queue, core3_queue = split_tasks_into_queues(tasks)

    # Create JobLists for each core
    JobList1 = create_job_list(core1_queue)
    JobList2 = create_job_list(core2_queue)
    JobList3 = create_job_list(core3_queue)

    # Prioritize jobs
    prioritize(JobList1, 2)
    prioritize(JobList2, 2)
    prioritize(JobList3, 2)

    # Write initial job lists to files
    write_job_list("jobList1", JobList1)
    write_job_list("jobList2", JobList2)
    write_job_list("jobList3", JobList3)

    # Create stop event for threads
    stop_event = threading.Event()

    # Initialize and start core threads
    threads = initialize_cores_and_threads(resources, [JobList1, JobList2, JobList3], stop_event)

    # mock data
    # wait_queue = [
    # Job(1, "JobA", 5, 1, 1, 5, 1),
    # Job(2, "JobB", 3, 1, 1, 5, 1),
    # Job(3, "JobC", 2, 1, 1, 5, 1),
    # Job(4, "JobD", 4, 1, 1, 6, 1),
    # Job(5, "JobE", 6, 1, 1, 6, 1),
    # Job(6, "JobF", 9, 1, 1, 7, 1),
    # Job(7, "JobG", 2, 1, 1, 8, 1),
    # Job(8, "JobH", 4, 1, 1, 9, 1),
    # Job(9, "JobI", 8, 1, 1, 10, 1),
    # Job(10, "JobJ", 5, 1, 1, 22, 1)
    # ]
    # x = 0
    # for j in wait_queue:
    #     j.arrival_wait_time = x
    #     x += 1
    
    # current time
    currTime = 0
    # Main loop to manage the wait queue
    curr_time = 0
    while True:
        # Receive the wait queue
        wait_queue = receive_wait_queue()
        time.sleep(0.1)

        # Dynamically read the job lists to get their current state
        JobList1 = receive_jobList("jobList1")
        JobList2 = receive_jobList("jobList2")
        JobList3 = receive_jobList("jobList3")

        # Check total jobs left in all cores
        total_jobs = len(JobList1) + len(JobList2) + len(JobList3)

        # Exit condition: wait queue is empty and no jobs left in cores
        if not wait_queue and total_jobs == 0:
            print("Wait queue is empty and no jobs left in cores, exiting...")
            terminate_threads(threads, stop_event)
            break

        # Process the wait queue and redistribute jobs
        process_wait_queue(wait_queue, [JobList1, JobList2, JobList3], curr_time)

        curr_time += 1

def split_tasks_into_queues(tasks):
    core1_queue, core2_queue, core3_queue = [None] * 5, [None] * 5, [None] * 5
    i, j, k = 0, 0, 0
    for t in tasks:
        core_id = t[-1]
        if core_id == '1':
            core1_queue[i] = t.split(' ')
            i += 1
        elif core_id == '2':
            core2_queue[j] = t.split(' ')
            j += 1
        else:
            core3_queue[k] = t.split(' ')
            k += 1
    return core1_queue, core2_queue, core3_queue

def create_job_list(core_queue):
    job_list = []
    job_id = 0
    for item in core_queue:
        if item:
            job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5])))
            job_id += 1
    return job_list

def prioritize(job_list, quantum):
    '''
    Prioritizes jobs based on their burst times and assigns them a quantum.
    '''
    if not job_list:
        # print("Error: Job list is empty. Skipping prioritization.")
        return
    # Find the first valid burst time as a reference
    first_quantum = next((job.burst_time for job in job_list if job.burst_time > 0), None)

    if first_quantum is None or first_quantum == 0:
        print("Error: No valid jobs with non-zero burst time found. Skipping prioritization.")
        return

    # Assign quantum to jobs based on burst time
    for job in job_list:
        job.quantum = max((job.burst_time * quantum) // first_quantum, 1)  # Ensure quantum is at least 1

    # sorted_job_list = sorted(job_list, key=lambda job: (-int(job.burst_time), int(job.arrival_time)))
    # priority = 1
    # first_quantum = int(sorted_job_list[0].burst_time)
    # quantum =  first_quantum // division_factor
    # calculate quantum for each job
    # for job in sorted_job_list:
    #     job.priority = priority
    #     job.quantum = (job.burst_time * quantum) // first_quantum
    #     priority += 1

    # print_debug(sorted_job_list)

def write_job_list(core_name, job_list):
    """Write job list to JSON file with proper synchronization"""
    with job_list_lock:
        try:
            # Read existing data
            try:
                with open(job_list_file, 'r') as file:
                    job_lists = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                job_lists = {'jobList1': [], 'jobList2': [], 'jobList3': []}
            
            # Update the specific core's job list
            job_lists[core_name] = [json.loads(json.dumps(job, cls=JobEncoder)) for job in job_list]
            
            # Write back to file
            with open(job_list_file, 'w') as file:
                json.dump(job_lists, file, indent=4)
        except Exception as e:
            print(f"Error writing to {core_name}: {str(e)}")

def initialize_cores_and_threads(resources, job_lists, stop_event):
    threads = []
    for i, job_list in enumerate(job_lists, start=1):
        thread = threading.Thread(target=handle_core, args=(f"jobList{i}", resources, stop_event))
        threads.append(thread)
        thread.start()
    return threads

def receive_wait_queue():
    '''
    Reads the wait queue from a file, ensuring mutual exclusion, and removes it after reading.
    '''
    with wait_queue_lock:
        try:
            with open(wait_queue_file, 'r') as file:
                content = file.read().strip()
                if not content:
                    return []
                wait_queues = json.loads(content)
                if not wait_queues:
                    return []
                wait_queue = wait_queues.pop()

                with open(wait_queue_file, 'w') as file:
                    json.dump(wait_queues, file, indent=4)

                return [Job(**job) for job in wait_queue]  # Convert dicts back to Job objects
        except FileNotFoundError:
            return []  # Return an empty list if the file does not exist
        except json.JSONDecodeError:
            print("Error: JSONDecodeError - The wait queue file is not properly formatted.")
            return []

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

def terminate_threads(threads, stop_event):
    stop_event.set()
    for thread in threads:
        thread.join()

def process_wait_queue(wait_queue, job_lists, current_time):
    top_three = handle_wait_queue(wait_queue, current_time)
    # for debug
    # print("Top Three Jobs:")
    # for job in top_three:
    # print(f"{job.name}: wait_time = {job.wait_time}")
    updated_job_lists = [receive_jobList(f"jobList{i}") for i in range(1, 4)]
    load_balancing(top_three, *updated_job_lists)
    # Write updated job lists back to the file
    for i, job_list in enumerate(updated_job_lists, start=1):
        write_job_list(f"jobList{i}", job_list)
    # Write updated wait queue back to the file
    write_wait_queue(wait_queue)
    # Debug: Print core states after load_balancing
    # print("\nCore States After Balancing:")
    # print(f"JobList1: {[job.name for job in JobList1]}")
    # print(f"JobList2: {[job.name for job in JobList2]}")
    # print(f"JobList3: {[job.name for job in JobList3]}")

def handle_core(core_name, resources, stop_event):
    '''
    Handles tasks for a specific core.
    '''
    current_time = 0
    # Read the job list for the core
    JobList = receive_jobList(core_name)
    # Scheduling using weighted round-robin for each core
    wrrList = weighted_round_robin(JobList)
    # print("Initial wrrList: ", wrrList)

    # Check resources and manage wait queue
    wait_queue = receive_wait_queue()

    while wrrList:
        # print("wrrList (current): ", wrrList)

        # Pop the next item in order
        popped_item = wrrList.pop(0)
        # print("popped item (ordered): ", popped_item)

        process_id = popped_item[1]

        # Process the job without fully removing it from JobList
        if process_id < len(JobList) and JobList[process_id] is not None:
            job_to_process = JobList[process_id]

        # Handle resource checks and execution
        if check_resource(resources, job_to_process):
            resources[0] -= job_to_process.resource1
            resources[1] -= job_to_process.resource2
            job_to_process.state = "Running"
            # print(f"Job {job_to_process.name} is running r1:{resources[0]} and r2:{resources[1]}")
            JobList[process_id].burst_time = job_to_process.burst_time - job_to_process.quantum
            execute_task(core_name, resources, job_to_process)
        else:
            job_to_process.state = "Waiting"
            wait_queue.append(job_to_process)
            print(f"Job {job_to_process.name} is waiting for resources.")

        # Write updated job list and wait queue back to the file
        write_job_list(core_name, JobList)
        write_wait_queue(wait_queue)

        current_time += 1

def load_balancing(top_three, jobList1, jobList2, jobList3):
    '''
    Balances the load by assigning jobs from top_three to the core queues
    in a way that ensures an even distribution of jobs among the cores.

    Arguments:
        top_three: List of jobs to be assigned.
        jobList1, jobList2, jobList3: Current jobs assigned to each core.

    Returns:
        Updated jobList1, jobList2, jobList3.
    '''
    # Calculate the current load on each core
    loads = {
        "jobList1": len([job for job in jobList1 if job is not None]),
        "jobList2": len([job for job in jobList2 if job is not None]),
        "jobList3": len([job for job in jobList3 if job is not None]),
    }

    # Sort cores by their current load in ascending order
    sorted_cores = sorted(loads.items(), key=lambda x: x[1])

    # Distribute jobs to the cores with the least load
    for job in top_three:
        # Always pick the core with the least load
        core_name, _ = sorted_cores[0]

        # Assign the job to the corresponding core and update the load
        if core_name == "jobList1":
            jobList1.append(job)
            loads["jobList1"] += 1
        elif core_name == "jobList2":
            jobList2.append(job)
            loads["jobList2"] += 1
        elif core_name == "jobList3":
            jobList3.append(job)
            loads["jobList3"] += 1

        # Re-sort the cores by their updated load
        sorted_cores = sorted(loads.items(), key=lambda x: x[1])

    return jobList1, jobList2, jobList3

def write_wait_queue(wait_queue):
    '''
    Writes the wait queue to a file, ensuring mutual exclusion.
    '''
    with wait_queue_lock:
        with open(wait_queue_file, 'w') as file:
            json.dump([job.__dict__ for job in wait_queue], file)  # Convert Job objects to dicts
        # print(f"Wait queue written to {wait_queue_file}: {[job.name for job in wait_queue]}")

def weighted_round_robin(job_list):
    ''' 
    Schedules jobs using a weighted round-robin algorithm.
    Input :
    def weighted_round_robin(jobList , quantum, core_ready_queue, wait_queue)

    Job properties:
           name    | burst time | resource1  | resource2  | arrival time |  CPU Dest  |  priority  |  quantum   |   state    |
           T12     |    100     |     0      |     1      |      0       |     2      |     1      |     50     |   Ready    |
    Job properties:
           name    | burst time | resource1  | resource2  | arrival time |  CPU Dest  |  priority  |  quantum   |   state    |
           T12     |     20     |     5      |     0      |      0       |     2      |     2      |     10     |   Ready    |
    Job properties:
           name    | burst time | resource1  | resource2  | arrival time |  CPU Dest  |  priority  |  quantum   |   state    |
           T12     |     5      |     6      |     0      |      0       |     2      |     3      |     2      |   Ready    |

    prioritize(inputList)
    calculating quantum based on priority and assign value to attributes Job.priority & Job.quantum

    core_ready_queue = []

    Expected Output :
        1. ProcessList = [1, 3, 5, 7, 8, 10, 12, 13, 15, 16, 17]
        a list of process pid's this list claims that first we should run P2 then P4 then P1 and so on

        2. Time Schedules = [1, 3, 5, 7, 8, 10, 12, 13, 15, 16, 17]
        a list of times indicated the time which we should switch contex from a process to anther process
    '''
    if not job_list:
        # print("Error: Job list is empty in weighted_round_robin.")
        return []

    schedule = []

    # Current system time
    current_time = 0

    # List of remaining tasks
    remaining_JobList = [job for job in job_list]

    # Continue until all tasks are finished
    while remaining_JobList:
        executed = False  # To check if a job has been completed

        for job in remaining_JobList[:]:  # Make a copy to prevent concurrent changes
            if job.arrival_time <= current_time:
                # How long this job can run
                time_slice = min(job.quantum, job.burst_time)

                # Record the start time and the job being executed
                schedule.append((current_time, job.id))

                # Update the current time and remaining burst time
                current_time += time_slice
                job.burst_time -= time_slice
                executed = True

                # If the job has finished, remove it from the list
                if job.burst_time <= 0:
                    remaining_JobList.remove(job)

        if not executed:
            # If no job was executed, advance the time to the next arrival_time
            current_time = min(job.arrival_time for job in remaining_JobList if job.arrival_time > current_time)

    return schedule

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

def handle_wait_queue(wait_queue, currTime):
    """Handle wait queue with proper None checks"""
    if not wait_queue or all(job is None for job in wait_queue):
        return []
    
    # Filter out None values and update wait times
    valid_jobs = [job for job in wait_queue if job is not None]
    for job in valid_jobs:
        if hasattr(job, 'arrival_wait_time'):
            if currTime - job.arrival_wait_time > 0:
                job.wait_time = currTime - job.arrival_wait_time
            else:
                job.wait_time = 0
    
    # Sort and get top three
    sorted_queue = sorted(valid_jobs, key=lambda item: item.wait_time, reverse=True)
    top_three = sorted_queue[:3]
    
    # Remove top three from wait queue
    for job in top_three:
        if job in wait_queue:
            wait_queue.remove(job)
    
    return top_three
