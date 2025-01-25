import threading
import json
import time
from subsystem1 import get_reources

wait_queue_file = "./wait_queues/wait_queue3.json"
job_list_file = "./ready_queues/ready_queue3.json"
output_file = "out.txt"

# Mutex locks
wait_queue_lock = threading.Lock()
job_list_lock = threading.Lock()

class Job:
    def __init__(self, id, name, burst_time, resource1, resource2, arrival_time, period, repetition, deadline, **kwargs):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.period = period
        self.repetition = repetition
        self.deadline = deadline
        self.remain_time = kwargs.get("remain_time", burst_time)
        self.state = kwargs.get("state", "Ready")  # Default state
    def __str__(self):
        return f""" Job properties:
        {"id":^10} | {"name":^10} | {"burst time":^10} | {"resource1":^10} | {"resource2":^10} |  {"period":^10} | {"arrival time":^12} |  {"repetition":^10} | {"deadline":^10} | {"state":^10} |
        {self.id:^10} | {self.name:^10} | {self.burst_time:^10} | {self.resource1:^10} | {self.resource2:^10} |  {self.period:^10} | {self.arrival_time:^12} |  {self.repetition:^10} | {self.deadline:^10} | {self.state:^10} |"""

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
                'period': obj.period,
                'repetition': obj.repetition,
                'deadline': obj.deadline,
                'remain_time': obj.remain_time,
                'state': obj.state
            }
        return super().default(obj)

# def handle_subSystem3(resources, tasks):
#     """
#         Handles SubSystem3 that has a ready queue and a wait queue.

#         Simulates the CPU core with a thread.
#     """

#     current_time = 0

#     # Initialize queue
#     JobList = []

#     for t in tasks:
#         JobList.append(t.split(' '))

#     # Scheduling using Rate Monotonic for the core
#     isschedulable, rm_schedule = rate_monotonic(JobList)

#     while not len(rm_schedule) == 0:
#         # Pop the next item in order
#         if(rm_schedule):
#             job_to_process = rm_schedule.pop(0)
#             print("popped item (ordered): ", job_to_process)
#             write_job_list(rm_schedule)
        
#         if(job_to_process[0] != "-"):
#             process_id = int(job_to_process[0])
#         else:
#             process_id = -1
#         print("process_id : " , process_id)
        
#         if process_id < len(JobList) and JobList[process_id] is not None:
#             job_to_process = JobList[process_id]

#         print("job_to_process : ", job_to_process.name)

#         if not isschedulable:
            

#         # Handle resource checks and execution
#         if not check_resource(resources, job_to_process):
#             print(2000*"#")
#             # borrow from other subsystems
#             r1 , r2 = borrow_resource()
#             print(f"we don't have resource for {job_to_process.name} in Sub3 so we got r1 : {r1} and r2 : {r2}")
#             # Add job_to_process to the head of rm_schedule
#             print(f"Job {job_to_process.name} is waiting for resources.")

#         resources[0] -= int(job_to_process[2])
#         resources[1] -= int(job_to_process[3])
#         # job_to_process.state = "Running"
#         print(f"Job {job_to_process[0]} is running r1:{resources[0]} and r2:{resources[1]}")
#         execute_task(resources, job_to_process)
#         # write_job_list(rm_schedule)
#         current_time += 1

def handle_subSystem3(resources, tasks):
    current_time = 0
    JobList = []

    for t in tasks:
        JobList.append(t.split(' '))

    isschedulable, rm_schedule = rate_monotonic(JobList)

    while not len(rm_schedule) == 0:
        if rm_schedule:
            job_to_process = rm_schedule.pop(0)
            print("popped item (ordered): ", job_to_process)
            write_job_list(rm_schedule)

        process_id = int(job_to_process[0]) if job_to_process[0] != "-" else -1
        if process_id < len(JobList) and JobList[process_id] is not None:
            job_to_process = JobList[process_id]

        print("job_to_process: ", job_to_process.name)

        # Case 1: Schedulable and have resource 
        if isschedulable and check_resource(resources, job_to_process):
            print("1")
            run_and_print_snapshot(resources, job_to_process, current_time)
        # Case 2: Not schedulable and have resource
        elif not isschedulable and check_resource(resources, job_to_process):
            print("2")
            if borrow_and_run(resources, job_to_process, only_borrow_one=True):
                run_and_print_snapshot(resources, job_to_process, current_time)
        # Case 3: Not schedulable and not have resource
        elif not isschedulable and not check_resource(resources, job_to_process):
            print("3")
            if borrow_and_run(resources, job_to_process, only_borrow_one=False):
                run_and_print_snapshot(resources, job_to_process, current_time)
        # Case 4: Schedulable and not have resource
        elif isschedulable and not check_resource(resources, job_to_process):
            print("4")
            if borrow_and_run(resources, job_to_process, only_borrow_one=False):
                run_and_print_snapshot(resources, job_to_process, current_time)

        current_time += 1

def borrow_and_run(resources, job_to_process, only_borrow_one):
    """
    Borrow resources from other subsystems to enable the task to run for half of its burst time.
    If only_borrow_one is True, attempt to borrow only one resource from each subsystem.
    Otherwise, borrow enough resources to meet the job's needs.
    """
    r1, r2 = get_reources()  # Get available resources from other subsystems
    needed_r1 = max(0, int(job_to_process[2]) - resources[0])
    needed_r2 = max(0, int(job_to_process[3]) - resources[1])

    if only_borrow_one:
        # Attempt to borrow just enough to run the task at half burst time
        if r1 >= 1 or r2 >= 1:
            resources[0] += 1
            resources[1] += 1
            return True
    else:
        # Borrow exactly what is needed
        if r1 >= needed_r1 and r2 >= needed_r2:
            resources[0] += needed_r1
            resources[1] += needed_r2
            return True

    return False

def run_and_print_snapshot(resources, job_to_process, current_time):
    """
    Run the task, consume resources, and print a snapshot of the system state to the output file.
    """
    resources[0] -= int(job_to_process[2])
    resources[1] -= int(job_to_process[3])
    job_to_process.state = "Running"

    # Simulate running for half of the burst time
    job_to_process.remain_time = max(0, job_to_process.remain_time - job_to_process.burst_time // 2)

    # Restore resources after running
    resources[0] += int(job_to_process[2])
    resources[1] += int(job_to_process[3])
    job_to_process.state = "Completed"

    # Print snapshot to out.txt
    with open(output_file, 'a') as f:
        f.write(f"Time = {current_time}\n")
        f.write(f"Sub3:\n\n")
        f.write(f"    Resources: R1: {resources[0]} R2: {resources[1]}\n")
        f.write(f"    Core1:\n")
        f.write(f"        Running Task: {job_to_process.name}\n")
        f.write(f"        Ready Queue: []\n\n")
        f.write("------------------------------------------------------------\n")

# def create_job_list(core_queue):
#     job_list = []
#     job_id = 0
#     deadline = 0
#     for i in range(len(core_queue)):
#         item = core_queue[i]
#         deadline = int(core_queue[i][4]) + int(core_queue[i][5])
#         if item:
#             job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5]), int(item[6]), deadline))
#             job_id += 1
#     return job_list

def rate_monotonic(tasks):
    """
    وظایف را براساس الگوریتم RMS زمان‌بندی می‌کند.

    tasks: لیستی از رشته‌های وظایف به فرمت 'T31 20 2 3 0 50 10'.
    خروجی:
    - True و برنامه زمان‌بندی اگر قابل زمان‌بندی باشد.
    - False و [] اگر زمان‌بندی‌پذیر نباشد.
    """
    # پارس کردن اطلاعات وظایف
    parsed_tasks = []
    id = -1;
    for task in tasks:
        id = id + 1;
        name = task[0]
        burst_time = int(task[1])
        resource1 = int(task[2])
        resource2 = int(task[3])
        arrival_time = int(task[4])
        period = int(task[5])
        repetition = int(task[6])
        deadline = period + arrival_time
        parsed_tasks.append({
            "id": id,
            "name": name,
            "burst_time": int(burst_time),
            "resource1": int(resource1),
            "resource2": int(resource2),
            "arrival_time": int(arrival_time),
            "period": int(period),
            "repetition": int(repetition),
            "remaining_repetition": int(repetition),
            "next_deadline": deadline,  # محاسبه ددلاین اولیه
        })
    # محاسبه بار کاری سیستم
    utilization = sum(task["burst_time"] / task["period"] for task in parsed_tasks)
    n = len(parsed_tasks)
    utilization_bound = n * (2 ** (1 / n) - 1)

    # بررسی قابلیت زمان‌بندی
    if utilization > utilization_bound:
        return False, []  # زمان‌بندی‌پذیر نیست

    # ایجاد جدول زمان‌بندی
    schedule = []
    current_time = 0
    total_tasks = sum(task["remaining_repetition"] for task in parsed_tasks)

    while total_tasks > 0:
        # یافتن وظیفه‌ای که باید اجرا شود
        parsed_tasks.sort(key=lambda x: (x["period"], x["next_deadline"]))  # اولویت براساس دوره تناوب و ددلاین
        task_scheduled = False

        for task in parsed_tasks:
            if task["remaining_repetition"] > 0 and current_time >= task["arrival_time"] and current_time + int(task["burst_time"]) <= int(task["next_deadline"]):
                # اجرای وظیفه
                execution_time = task["burst_time"]
                schedule.append((task["id"], execution_time))
                current_time += execution_time
                task["remaining_repetition"] -= 1
                task["arrival_time"] += task["period"]  # به‌روزرسانی زمان ورود بعدی
                task["next_deadline"] += task["period"]  # به‌روزرسانی ددلاین بعدی
                task_scheduled = True
                total_tasks -= 1
                break

        if not task_scheduled:
            # وقتی وظیفه‌ای برای اجرا وجود ندارد
            if schedule and schedule[-1][0] == '-':
                schedule[-1] = ('-', schedule[-1][1] + 1)
            else:
                schedule.append(('-', 1))
            current_time += 1

    return True, schedule

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

def load_balancing(top_three, job_list):
    '''
    Balances the load by assigning jobs from top_three to the core queue
    in a way that ensures an even distribution of jobs among the cores.
    '''
    for job in top_three:
        job_list.append(job)

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
    '''
    return resources[0] >= int(job_to_process[2]) and resources[1] >= int(job_to_process[3])

def execute_task(resources, job_to_process):
    '''
    execute task on core and print snapShot of system

    print_snapshot()
    '''
    resources[0] += int(job_to_process[2])
    resources[1] += int(job_to_process[3])

def print_snapshot(curr_time, job_list, wait_queue):
    '''
    Print snapshot of the system's state.
    '''
    print(f"Time: {curr_time}")
    print("Job List:")
    for job in job_list:
        print(job)
    print("Wait Queue:")
    for job in wait_queue:
        print(job)