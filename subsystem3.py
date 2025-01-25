import threading
import json
import time

wait_queue_file = "wait_queue3.json"
job_list_file = "job_list3.json"

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

def handle_subSystem3(resources, tasks):
    """
        Handles SubSystem3 that has a ready queue and a wait queue.

        Simulates the CPU core with a thread.
    """
    # Initialize queue
    core_queue = []

    for t in tasks:
        core_queue.append(t.split(' '))
    
    # Create JobList for the core
    JobList = create_job_list(core_queue)

    # Write initial job list to file
    write_job_list(JobList)

    # Create stop event for thread
    stop_event = threading.Event()

    # Initialize and start core thread
    thread = threading.Thread(target=handle_core, args=(resources, stop_event))
    thread.start()

    # Main loop to manage the wait queue
    curr_time = 0
    while True:
        # Receive the wait queue
        wait_queue = receive_wait_queue()

        # Dynamically read the job list to get its current state
        JobList = read_job_list()

        # Check total jobs left in the core
        total_jobs = len(JobList)

        # Exit condition: wait queue is empty and no jobs left in core
        if not wait_queue and total_jobs == 0:
            print("Wait queue is empty and no jobs left in core, exiting...")
            stop_event.set()
            thread.join()
            break

        # Print snapshot of the system's state
        # print_snapshot(curr_time, JobList, wait_queue)

        curr_time += 1
        # time.sleep(1)  # Simulate time unit

def create_job_list(core_queue):
    job_list = []
    job_id = 0
    deadline = 0
    for i in range(len(core_queue)):
        item = core_queue[i]
        print(item)
        deadline = int(core_queue[i][4]) + int(core_queue[i][5])
        if item:
            job_list.append(Job(job_id, item[0], int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5]), int(item[6]), deadline))
            job_id += 1
    return job_list

def handle_core(resources, stop_event):
    '''
    Handles tasks for the core.
    '''
    # current_time = 0

    # Read the job list for the core
    JobList = read_job_list()

    # Scheduling using Rate Monotonic for the core
    rm_schedule = rate_monotonic(JobList)
    print("schedule: ", rm_schedule)


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
    for task in tasks:
        name = task.name
        burst_time = task.burst_time
        resource1 = task.resource1
        resource2 = task.resource2
        arrival_time = task.arrival_time
        period = task.period
        repetition = task.repetition
        deadline = task.deadline
        parsed_tasks.append({
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

    for item in parsed_tasks:
        print(item)
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
            if task["remaining_repetition"] > 0 and current_time >= task["arrival_time"] and current_time + task["burst_time"] <= task["next_deadline"]:
                # اجرای وظیفه
                execution_time = task["burst_time"]
                schedule.append((task["name"], execution_time))
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

def receive_wait_queue():
    '''Reads the wait queue from a file, ensuring mutual exclusion, and removes it after reading.'''
    with wait_queue_lock:
        try:
            with open(wait_queue_file, 'r') as file:
                content = file.read().strip()
                if not content:
                    return []
                wait_queues = json.loads(content)
                if not wait_queues:
                    return []
                wait_queue = wait_queues.pop(0)  # Assuming wait_queues is a list of queues

                # Make sure the items in wait_queue are dictionaries
                if not all(isinstance(job, dict) for job in wait_queue):
                    print(f"Data format error: Expected dictionaries but got {type(wait_queue[0]) if wait_queue else 'empty list'}")
                    return []

                with open(wait_queue_file, 'w') as file:
                    json.dump(wait_queues, file, indent=4)

                return [Job(**job) for job in wait_queue]  # Ensure this only runs if all jobs are dicts
        except FileNotFoundError:
            print("FileNotFoundError: The wait queue file does not exist.")
            return []
        except json.JSONDecodeError:
            print("JSONDecodeError: The wait queue file is not properly formatted.")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []

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