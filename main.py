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
    def __init__(self, arrival_time, burst_time):
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remain_time = burst_time
        self.current_time = 0
        self.total_arrival_time = 0
        self.wait_time = 0

    def __str__(self):
        return f"{self.current_time}\t\t{self.total_arrival_time}\t\t\t{self.wait_time}"

# near future...
def handle_subSystem1(resources, tasks):
    core1_queue = list()
    core2_queue = list()
    core3_queue = list()

    for t in tasks:
        length = len(t)
        if t[length - 1] == '1':
            core1_queue.append(t.split(' '))
        elif t[length - 1] == '2':
            core2_queue.append(t.split(' '))
        else:
            core3_queue.append(t.split(' '))

    print("core1_queue = " , core1_queue)
    print("core2_queue = " , core2_queue)
    print("core3_queue = " , core3_queue)

    jobs = [
        Job(1, 3),
        Job(1, 5),
        Job(5, 3),
        Job(5, 1),
        Job(6, 2),
        Job(7, 3)
    ]

    # core1_length = len(core1_queue)
    # for item in core1_queue:
    #     jobs.append(Job(item[1] , item[core1_length - 1]))

    # core2_length = len(core2_queue)
    # for item in core2_queue:
    #     jobs.append(Job(item[1] , item[core2_length - 1]))
    
    # core3_length = len(core3_queue)
    # for item in core3_queue:
    #     jobs.append(Job(item[1] , item[core3_length - 1]))
    

    quantum = 2
    # scheduling using round robin algorithm
    print("Completion\tTurnaround\tWaiting")
    cur_time = 0
    total_bt = sum([p.burst_time for p in jobs])
    rem_bt = total_bt
    queue = []

    while rem_bt > 0:
        for job in jobs:
            if job.arrival_time <= cur_time and job not in queue and job.remain_time > 0:
                queue.append(job)

        if len(queue) == 0:
            cur_time += 1
            continue

        next_job = queue.pop(0)
        if next_job.remain_time > quantum:
            cur_time += quantum
            next_job.remain_time -= quantum
        else:
            cur_time += next_job.remain_time
            rem_bt -= next_job.remain_time
            next_job.remain_time = 0
            next_job.current_time = cur_time
            next_job.total_arrival_time = next_job.current_time - next_job.arrival_time
            next_job.wait_time = next_job.total_arrival_time - next_job.burst_time
            print(next_job)

        for job in jobs:
            if job.remain_time > 0 and job.arrival_time <= cur_time and job not in queue and job != next_job:
                queue.append(job)

        # print("rem_bt = " , rem_bt)

    # near future
    # threadCore1 = threading.Thread(target=handle_subSystem1, args=(allsubSystemResourses[0], allsubSystemTasks[0]))
    # threadCore2 = threading.Thread(target=handle_subSystem2, args=(allsubSystemResourses[1], allsubSystemTasks[1]))
    # threadCore3 = threading.Thread(target=handle_subSystem3, args=(allsubSystemResourses[2], allsubSystemTasks[2]))

    # # Wait for all threads to complete
    # threadCore1.join()
    # threadCore2.join()
    # threadCore3.join()


def handle_subSystem2(resources, tasks):
   pass

def handle_subSystem3(resources, tasks):
    pass

def handle_subSystem4(resources, tasks):
    pass

if __name__ == "__main__":
    main()

