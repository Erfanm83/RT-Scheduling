import threading
import time

allsubSystemResourses = []
allsubSystemTasks = []

def main():
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
    def __init__(self, id ,name, burst_time, resource1, resource2, arrival_time, CPU_dest):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.CPU_dest = CPU_dest
        self.remain_time = burst_time
        self.current_time = 0
        self.total_arrival_time = 0
        self.wait_time = 0
        self.arrival_wait_time = 0
        self.priority = 0
        self.quantum = 0
        self.state = "Ready" # can be "Running" or "Waiting" or "Ready"  

    def __str__(self):
        return f""" Job properties:
        {"id":^10} | {"name":^10} | {"burst time":^10} | {"resource1":^10} | {"resource2":^10} | {"arrival time":^12} | {"CPU Dest":^10} | {"priority":^10} | {"quantum":^10} | {"state":^10} |
        {self.id:^10} | {self.name:^10} | {self.burst_time:^10} | {self.resource1:^10} | {self.resource2:^10} | {self.arrival_time:^12} | {self.CPU_dest:^10} | {self.priority:^10} | {self.quantum:^10} | {self.state:^10} |"""

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

    # threadCore1 = threading.Thread(target= handle_core, args=(JobList1)).start()
    # threadCore2 = threading.Thread(target= handle_core, args=(JobList2)).start()
    # threadCore3 = threading.Thread(target= handle_core, args=(JobList3)).start()

    # mock data
    wait_queue = [
    Job(1, "JobA", 5, 1, 1, 5, 1),
    Job(2, "JobB", 3, 1, 1, 5, 1),
    Job(3, "JobC", 2, 1, 1, 5, 1),
    Job(4, "JobD", 4, 1, 1, 6, 1),
    Job(5, "JobE", 6, 1, 1, 6, 1),
    Job(6, "JobF", 9, 1, 1, 7, 1),
    Job(7, "JobG", 2, 1, 1, 8, 1),
    Job(8, "JobH", 4, 1, 1, 9, 1),
    Job(9, "JobI", 8, 1, 1, 10, 1),
    Job(10, "JobJ", 5, 1, 1, 22, 1)
    ]

    x = 0
    for j in wait_queue:
        j.arrival_wait_time = x
        x += 1

    # Example current time
    currTime = 20

    while True:
        # receiving wait queue
        # wait_queue = receive_wait_queue()

        # calculating the amount of time of each process in wait queue 
        top_three = handle_wait_queue(wait_queue, currTime)

        print("Top Three Jobs:")
        for job in top_three:
            print(f"{job.name}: wait_time = {job.wait_time}")
        
        # we need to check if there are available space in each core
        load_balancing(top_three, JobList1, JobList2, JobList3)

        currTime += 1

        # Exit Condition
        if not (wait_queue):
            print("Exiting from main loop...")
            # Wait for all threads to complete
            # threadCore1.join()
            # threadCore2.join()
            # threadCore3.join()
            break

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
    prioritize(job_list, 2)

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

def prioritize(job_list, division_factor):
    sorted_job_list = sorted(job_list, key=lambda job: (-int(job.burst_time), int(job.arrival_time)))

    priority = 1
    first_quantum = int(sorted_job_list[0].burst_time)
    quantum =  first_quantum // division_factor
    # calculate quantum for each job
    for job in sorted_job_list:
        job.priority = priority
        job.quantum = (job.burst_time * quantum) // first_quantum
        priority += 1

    print_debug(sorted_job_list)

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

def handle_wait_queue(wait_queue, currTime):
    '''
    Implementing a mechanism to avoid starvation by calculating the amount of time waited in the queue
    and removing the top three processes.
    '''
    # Update the wait_time field for each job in the wait_queue
    for job in wait_queue:
        if currTime - job.arrival_wait_time > 0:
            job.wait_time = currTime - job.arrival_wait_time
        else:
            job.wait_time = 0

    # Print results
    # print("Remaining Wait Queue:")
    # for job in wait_queue:
    #     print(f"Job {job.name}: wait_time = {job.wait_time}")

    # Sort wait_queue based on wait_time in descending order
    sorted_queue = sorted(wait_queue, key=lambda item: item.wait_time, reverse=True)

    # Get the top three elements
    top_three = sorted_queue[:3]

    # Remove these top three elements from the wait_queue
    for job in top_three:
        wait_queue.remove(job)

    return top_three

def handle_core(JobList, R1, R2, wait_queue):
    while(True):
        # scheduling using round robin algorithm for each core
        wrrList = weighted_round_robin(JobList)

        # check resources for three tasks selected from WRR
        check_resource(R1 , R2, wrrList, JobList, wait_queue)

        # Exit Condition
        if not (wrrList):
            print("Exiting from core's thread loop...")
            break

def receive_wait_queue():
    pass

def load_balancing(top_three, jobList1, jobList2, jobList3):
    '''
    Balances the load by assigning jobs from top_three to the core queues
    based on their free space.

    Arguments:
        top_three: List of jobs to be assigned.
        jobList1, jobList2, jobList3: Current jobs assigned to each core.

    Returns:
        Updated jobList1, jobList2, jobList3.
    '''
    free_space = {
        "jobList1": jobList1.count(None),
        "jobList2": jobList2.count(None),
        "jobList3": jobList3.count(None)
    }

    # Sort cores by free space in descending order
    sorted_cores = sorted(free_space.items(), key=lambda x: x[1], reverse=True)

    # Distribute jobs to the cores based on priority
    for job in top_three:
        for core_name, available_space in sorted_cores:
            if core_name == "jobList1" and free_space["jobList1"] >= job.wait_time:
                jobList1.append(job)
                free_space["jobList1"] -= job.wait_time
                break
            elif core_name == "jobList2" and free_space["jobList2"] >= job.wait_time:
                jobList2.append(job)
                free_space["jobList2"] -= job.wait_time
                break
            elif core_name == "jobList3" and free_space["jobList3"] >= job.wait_time:
                jobList3.append(job)
                free_space["jobList3"] -= job.wait_time
                break
    
    return jobList1, jobList2, jobList3

def print_debug(jobList):
    for i in range(len(jobList)):
        print(jobList[i])

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

