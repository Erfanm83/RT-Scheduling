import threading
import time

# Global variables for resources and tasks
all_subsystem_resources = []
all_subsystem_tasks = []

class Task:
    def __init__(self, name, burst_time, r1, r2, arrival_time, cpu_dest):
        self.name = name
        self.burst_time = int(burst_time)
        self.remaining_time = int(burst_time)
        self.r1 = int(r1)
        self.r2 = int(r2)
        self.arrival_time = int(arrival_time)
        self.cpu_dest = int(cpu_dest)
        self.state = "Ready"

    def __str__(self):
        return f"Task: {self.name}, Burst: {self.burst_time}, R1: {self.r1}, R2: {self.r2}, Arrival: {self.arrival_time}, CPU: {self.cpu_dest}, State: {self.state}"

def main():
    read_data_from_file()

    # Create and start threads for subsystems
    threads = []
    threads.append(threading.Thread(target=handle_subsystem1, args=(all_subsystem_resources[0], all_subsystem_tasks[0])))
    threads.append(threading.Thread(target=handle_subsystem2, args=(all_subsystem_resources[1], all_subsystem_tasks[1])))
    threads.append(threading.Thread(target=handle_subsystem3, args=(all_subsystem_resources[2], all_subsystem_tasks[2])))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("All subsystems have completed execution.")

def read_data_from_file():
    global all_subsystem_resources, all_subsystem_tasks

    with open("./in.txt", 'r') as file:
        # Read subsystem resources
        for _ in range(3):
            line = file.readline().strip()
            resources = list(map(int, line.split()))
            all_subsystem_resources.append(resources)

        # Read subsystem tasks
        for _ in range(3):
            subsystem_tasks = []
            while True:
                line = file.readline().strip()
                if line == "$":
                    break
                parts = line.split()
                task = Task(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
                subsystem_tasks.append(task)
            all_subsystem_tasks.append(subsystem_tasks)

def handle_subsystem1(resources, tasks):
    print("Handling Subsystem 1")
    cores = {1: [], 2: [], 3: []}  # Queues for each core

    for task in tasks:
        cores[task.cpu_dest].append(task)

    for core, queue in cores.items():
        print(f"Core {core} Queue: {[str(task) for task in queue]}")

    weighted_round_robin(cores, 2)

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

def weighted_round_robin(cores, quantum):
    time_unit = 0
    while any(core for core in cores.values()):
        for core_id, queue in cores.items():
            if not queue:
                continue

            task = queue.pop(0)
            execute_time = min(quantum, task.remaining_time)
            task.remaining_time -= execute_time
            time_unit += execute_time

            print(f"Time: {time_unit}, Core {core_id} executing {task.name}, Remaining: {task.remaining_time}")

            if task.remaining_time > 0:
                queue.append(task)

def execute_task(task):
    print(f"Executing {task.name} for {task.remaining_time} units")
    time.sleep(task.remaining_time / 10)  # Simulate execution
    task.state = "Completed"
    print(f"Task {task.name} completed.")

if __name__ == "__main__":
    main()
