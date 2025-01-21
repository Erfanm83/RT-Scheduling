import threading

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
        name, burst_time, resource1, resource2, arrival_time = task.split()
        parsed_tasks.append({
            "name": name,
            "burst_time": int(burst_time),
            "resource1": int(resource1),
            "resource2": int(resource2),
            "arrival_time": int(arrival_time),
            "remain_time": int(burst_time)
        })

    # print(parsed_tasks)

    time = 0
    schedule = []
    while parsed_tasks:
        # Filter tasks that have arrived
        available_tasks = [task for task in parsed_tasks if task["arrival_time"] <= time]
        if not available_tasks:
            time += 1
            continue

        # Sort by remaining time
        available_tasks.sort(key=lambda x: x["remain_time"])

        # Select the task with the shortest remaining time
        current_task = available_tasks[0]
        start_time = time
        if current_task["remain_time"] > 0:
            current_task["remain_time"] -= 1
            time += 1

        schedule.append(f"{current_task['name']} {time - start_time}")

        # If the task is completed, remove it from the list
        if current_task["remain_time"] == 0:
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
            combined_schedule.append(f"{current_task} {current_duration}")
            current_task = task
            current_duration = duration

    if current_task is not None:
        combined_schedule.append(f"{current_task} {current_duration}")

    return combined_schedule

def handle_subsystem2(resources, tasks):
    print("Handling Subsystem 2")
    print(tasks)
    print(resources)
    schedule = Shortest_Remaining_Time_First(tasks)  # Shortest Remaining Time First

    print("Schedule:" + str(schedule))

    # Create job list for the subsystem
    job_list_subsystem2 = []
    for i, task in enumerate(tasks):
        job_list_subsystem2.append(Job(i, task.name, task.burst_time, task.resource1, task.resource2, task.arrival_time))

    for job in job_list_subsystem2:
        print(job)

    condition = threading.Condition()

    # Start threads for the cores
    core1_thread = threading.Thread(target=core_execution, args=(1, job_list_subsystem2, resources, condition))
    core2_thread = threading.Thread(target=core_execution, args=(2, job_list_subsystem2, resources, condition))

    core1_thread.start()
    core2_thread.start()

    # Deadlock detection and resolution
    while core1_thread.is_alive() or core2_thread.is_alive():
        with condition:
            deadlock_job_id = detect_deadlock(job_list_subsystem2)
            if deadlock_job_id is not None:
                resolve_deadlock(job_list_subsystem2, deadlock_job_id)
            condition.notify_all()
            condition.wait(timeout=5)  # Check for deadlock every 5 seconds

    core1_thread.join()
    core2_thread.join()