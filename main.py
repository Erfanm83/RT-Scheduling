import threading
import time
import os
import json

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
    # print("Subsystem Resources:")
    read_data_from_file()
    # for res in allsubSystemResourses:
    #     print(res)
    
    # print("\nSubsystem Tasks:")
    # for idx, tasks in enumerate(allsubSystemTasks):
    #     print(f"Subsystem {idx + 1} Tasks:")
    #     for task in tasks:
    #         print(f"  {task}")

    # Creating subsystem handler threads
    thread1 = threading.Thread(target= handle_subSystem1, args=(allsubSystemResourses[0], allsubSystemTasks[0])).start()
    # near future...
    # thread2 = threading.Thread(target= handle_subSystem2).start()
    # thread3 = threading.Thread(target= handle_subSystem3).start()
    # thread4 = threading.Thread(target= handle_subSystem4).start()

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

# near future...
def handle_subSystem1(resources, tasks):
    '''
    handles SubSystem1 that has 3 ready queues and 1 wait queue

    simulating each core of CPU with a thread

    main thread manages the 3 Threads by receiving wait queue and pours joblists

    each thread schedules and executes processes and then printing them at out.txt 
    '''
    # fixed size lists
    wait_queue = [None] * 10
    core1_queue = [None] * 5
    core2_queue = [None] * 5
    core3_queue = [None] * 5
    i = 0
    j = 0
    k = 0

    # splitting core Tasks based on their Core destination
    for t in tasks:
        length = len(t)
        if t[length - 1] == '1':
            core1_queue[i] = t.split(' ')
            i += 1
        elif t[length - 1] == '2':
            core2_queue[j] = t.split(' ')
            j += 1
        else:
            core3_queue[k] = t.split(' ')
            k += 1

    # creating JobList for each core
    JobList1 = []
    JobList2 = []
    JobList3 = []
    id = 0
    for item in core1_queue:
        if item != None:
            JobList1.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
            id += 1
    id = 0
    for item in core2_queue:
        if item != None:
            JobList2.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
            id += 1
    id = 0
    for item in core3_queue:
        if item != None:
            JobList3.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
            id += 1

    # for debug
    # print_debug(JobList1)
    # print_debug(JobList2)
    # print_debug(JobList3)

    # Write initial job lists to the file
    write_job_list("jobList1", JobList1)
    write_job_list("jobList2", JobList2)
    write_job_list("jobList3", JobList3)

    # Start threads for each core
    threadCore1 = threading.Thread(target=handle_core, args=("jobList1", resources[0], resources[1]))
    threadCore2 = threading.Thread(target=handle_core, args=("jobList2", resources[0], resources[1]))
    threadCore3 = threading.Thread(target=handle_core, args=("jobList3", resources[0], resources[1]))
    # Start threads
    threads = [threadCore1, threadCore2, threadCore3]
    for thread in threads:
        thread.start()

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

    # Main loop
# while True:
    # Read the wait queue
    # wait_queue = receive_wait_queue()

    # calculating the amount of time of each process in wait queue 
    top_three = handle_wait_queue(wait_queue, currTime)

    # for debug
    # print("Top Three Jobs:")
    # for job in top_three:
    #     print(f"{job.name}: wait_time = {job.wait_time}")

    # Debug: Print core states before load_balancing‍
    # print("Core States Before Balancing:")
    # print(f"JobList1: {[job.name for job in JobList1]}")
    # print(f"JobList2: {[job.name for job in JobList2]}")
    # print(f"JobList3: {[job.name for job in JobList3]}")

    # Distribute the jobs to cores
    # JobList1 = receive_jobList("jobList1")
    # JobList2 = receive_jobList("jobList2")
    # JobList3 = receive_jobList("jobList3")
    # load_balancing(top_three, JobList1, JobList2, JobList3)


    # Write updated job lists back to the file
    # write_job_list("jobList1", JobList1)
    # write_job_list("jobList2", JobList2)
    # write_job_list("jobList3", JobList3)

    # Write updated wait queue back to the file
    # write_wait_queue(wait_queue)

    # Debug: Print core states after load_balancing
    # print("\nCore States After Balancing:")
    # print(f"JobList1: {[job.name for job in JobList1]}")
    # print(f"JobList2: {[job.name for job in JobList2]}")
    # print(f"JobList3: {[job.name for job in JobList3]}")

    currTime += 1

    # Exit Condition
    # if not (wait_queue):
    #     print("Wait queue is empty, exiting from main loop...")
        # Wait for all threads to complete
        # break

    # Wait for threads to complete
    threadCore1.join()
    threadCore2.join()
    threadCore3.join()

def handle_subsystem2(resources, tasks):
    print("Handling Subsystem 2")
    tasks.sort(key=lambda x: x.remaining_time)  # Shortest Remaining Time First
    for task in tasks:
        print(task)

    while tasks:
        task = tasks.pop(0)
        execute_task(task)

def handle_subsystem3(resources, tasks):
    print("Handling Subsystem 3")
    for task in tasks:
        print(task)

    for task in tasks:
        if task.remaining_time > 0:
            print(f"Executing Task: {task.name}")
            execute_task(task)

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
        print("Error: Job list is empty in weighted_round_robin.")
        return []

    print("\n[DEBUG] Job List Before Prioritization:")
    for job in job_list:
        print(f"ID: {job.id}, Burst Time: {job.burst_time}, Quantum: {job.quantum}")

    prioritize(job_list, 2)

    print("\n[DEBUG] Job List After Prioritization:")
    for job in job_list:
        print(f"ID: {job.id}, Burst Time: {job.burst_time}, Quantum: {job.quantum}")

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

def prioritize(job_list, quantum):
    '''
    Prioritizes jobs based on their burst times and assigns them a quantum.
    '''
    if not job_list:
        print("Error: Job list is empty. Skipping prioritization.")
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

# should be more generelize and return True or False depending on available resource
# and resource of the subsyem should be given in the input.
# def check_resource(R1 , R2, givenList, jobList, wait_queue)
def check_resource(R1 , R2, wrrList, jobList, wait_queue):
    '''
    check whether resources can meet the needs of task or not

    if YES, put them to cores and execute the task

    if NO, put them to wait queue

    '''
    while wrrList:
        popped_item = wrrList.pop(0)
        process_id = popped_item[1]
        job_to_process = jobList[process_id]
        if 0 <= R1 - job_to_process.resource1 and 0 <= R2 - job_to_process.resource2:
            # we have enough resources, assign it to CPU
            R1 -= job_to_process.resource1
            R2 -= job_to_process.resource2
            job_to_process.state = "Running"
            # run the task on CPU
        else:
            # we don't have enough resources, put it to wait queue
            job_to_process.state = "Waiting"
            wait_queue.append(job_to_process)

def execute_task(core, task):
    '''
    execute task on core and print snapShot of system

    print_snapshot()
    '''
    pass


# can be used in both subsystem 1 and 3 and 4
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

def handle_core(core_name, R1, R2):
    '''
    Handles tasks for a specific core.
    '''
    # while(True):
    # Read the job list for the core
    JobList = receive_jobList(core_name)

    if not JobList:
        # Exit if the job list is empty
        print(f"{core_name} job list is empty, exiting...")
        # break

    # scheduling using round robin algorithm for each core
    wrrList = weighted_round_robin(JobList)

    # Check resources and manage wait queue
    wait_queue = receive_wait_queue()
    check_resource(R1 , R2, wrrList, JobList, wait_queue)

    # Write updated job list and wait queue back to the file
    write_job_list(core_name, JobList)
    write_wait_queue(wait_queue)

def receive_wait_queue():
    '''
    Reads the wait queue from a file, ensuring mutual exclusion.
    '''
    with wait_queue_lock:
        try:
            with open(wait_queue_file, 'r') as file:
                content = file.read().strip()
                if not content:
                    return []
                wait_queue = json.loads(content)
            return [Job(**job) for job in wait_queue]  # Convert dicts back to Job objects
        except FileNotFoundError:
            return []  # Return an empty list if the file does not exist
        except json.JSONDecodeError:
            print("Error: JSONDecodeError - The wait queue file is not properly formatted.")
            return []

def write_wait_queue(wait_queue):
    '''
    Writes the wait queue to a file, ensuring mutual exclusion.
    '''
    with wait_queue_lock:
        with open(wait_queue_file, 'w') as file:
            json.dump([job.__dict__ for job in wait_queue], file)  # Convert Job objects to dicts

def receive_jobList(core_name):
    """Read job list from JSON file with proper synchronization"""
    with job_list_lock:
        try:
            with open(job_list_file, 'r') as file:
                content = file.read().strip()
                if not content:
                    return []
                job_lists = json.loads(content)
                job_data = job_lists.get(core_name, [])
                return [Job(**job) for job in job_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

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

def read_job_list(filename):
    try:
        with open(f"{filename}.json", 'r') as file:
            data = json.load(file)
            return [Job(**job_data) for job_data in data]
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return []

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

def print_debug(jobList):
    for i in range(len(jobList)):
        print(jobList[i])

def rate_monotonic(jobList):
    '''
    rate monotic scheduling of incoming jobs in the jobList

    returns a list of Jobs that scheduled jobs with rate_monotonic scheduling algorithm
    '''
    pass

def fcfs(jobList):
    '''
    schedule jobs based on first come first service algorithm
    return the scheduled list
    '''
    pass

def print_snapshot(current_time, resources, wait_queue, JobList1, JobList2, JobList3):
    with open("out.txt", "a") as file:
        file.write(f"Time = {current_time}\n\n")
        file.write(f"Sub1:\n\n")
        file.write(f"    Resources: R1: {resources[0]}  R2: {resources[1]}\n")
        file.write(f"    Waiting Queue: {[(job.name, job.id) for job in wait_queue]}\n")

        for idx, core_JobList in enumerate([JobList1, JobList2, JobList3], start=1):
            file.write(f"    Core{idx}:\n")
            running_task = next(((job.name, job.id) for job in core_JobList if job.state == "Running"), None)
            ready_queue = [(job.name, job.id) for job in core_JobList if job.state == "Ready"]
            file.write(f"        Running Task: {running_task if running_task else 'None'}\n")
            file.write(f"        Ready Queue: {ready_queue}\n")

        file.write("\n" + "-" * 70 + "\n")

if __name__ == "__main__":
    main()

