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
    wait_queue = list()
    core1_queue = list()
    core2_queue = list()
    core3_queue = list()

    # creating jobs for each core
    for t in tasks:
        length = len(t)
        if t[length - 1] == '1':
            core1_queue.append(t.split(' '))
        elif t[length - 1] == '2':
            core2_queue.append(t.split(' '))
        else:
            core3_queue.append(t.split(' '))
    jobs1 = []
    jobs2 = []
    jobs3 = []
    id = 0
    for item in core1_queue:
        jobs1.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
        id += 1
    id = 0
    for item in core2_queue:
        jobs2.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
        id += 1
    id = 0
    for item in core3_queue:
        jobs3.append(Job(id , item[0],int(item[1]),int(item[2]),int(item[3]),int(item[4]),int(item[5])))
        id += 1

    # for debug
    # print_debug(jobs1)
    # print_debug(jobs2)
    # print_debug(jobs3)
    
    # scheduling using round robin algorithm for each core
    wrrList1 = weighted_round_robin(jobs1)
    wrrList2 = weighted_round_robin(jobs2)
    wrrList3 = weighted_round_robin(jobs3)

    # check resources for three tasks selected from WRR
    check_resource(resources[0] , resources[1], wrrList1, jobs1, wait_queue)
    check_resource(resources[0] , resources[1], wrrList2, jobs2, wait_queue)
    check_resource(resources[0] , resources[1], wrrList3, jobs3, wait_queue)

    # near future...
    waited_job = wait_queue_algorithm()
    load_balancing()
    # we need to check if there are more tasks in the queue with enough resources
    # if there are, we can execute them here

    # core = list()
    # if result == True:
    #     threadCore1 = threading.Thread(target=execute_task, args=(core, selected_job))
    #     threadCore2 = threading.Thread(target=execute_task, args=(core, selected_job))
    #     threadCore3 = threading.Thread(target=execute_task, args=(core, selected_job))

    #     # Wait for all threads to complete
    #     # threadCore1.join()
    #     # threadCore2.join()
    #     # threadCore3.join()
    # else:
    #     wait_queue.append(selected_job)
    #     waited_job = wait_queue_algorithm()
    #     load_balancing(waited_job)

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

    if yes, put them to cores and execute the task
    if no, put them to wait queue
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

def wait_queue_algorithm():
    pass

def load_balancing():
    '''
    determine which core to put task
    '''
    pass

def print_debug(jobList):
    for i in range(len(jobList)):
        print(jobList[i])

def print_snapshot(current_time, resources, wait_queue, jobs1, jobs2, jobs3):
    with open("out.txt", "a") as file:
        file.write(f"Time = {current_time}\n\n")
        file.write(f"Sub1:\n\n")
        file.write(f"    Resources: R1: {resources[0]}  R2: {resources[1]}\n")
        file.write(f"    Waiting Queue: {[(job.name, job.id) for job in wait_queue]}\n")

        for idx, core_jobs in enumerate([jobs1, jobs2, jobs3], start=1):
            file.write(f"    Core{idx}:\n")
            running_task = next(((job.name, job.id) for job in core_jobs if job.state == "Running"), None)
            ready_queue = [(job.name, job.id) for job in core_jobs if job.state == "Ready"]
            file.write(f"        Running Task: {running_task if running_task else 'None'}\n")
            file.write(f"        Ready Queue: {ready_queue}\n")

        file.write("\n" + "-" * 70 + "\n")

if __name__ == "__main__":
    main()

