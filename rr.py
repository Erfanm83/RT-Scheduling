class Job:
    def __init__(self, pid, at, bt):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.rt = bt
        self.ct = 0
        self.tat = 0
        self.wt = 0

    def __str__(self):
        return f"{self.pid}\t\t{self.ct}\t\t{self.tat}\t\t\t{self.wt}"

def round_robin(jobs, quantum):
    print("\nJob\tCompletion\tTurnaround\tWaiting")
    cur_time = 0
    total_bt = sum([p.bt for p in jobs])
    rem_bt = total_bt
    queue = []

    while rem_bt > 0:
        for job in jobs:
            if job.at <= cur_time and job not in queue and job.rt > 0:
                queue.append(job)

        if len(queue) == 0:
            cur_time += 1
            continue

        next_job = queue.pop(0)
        if next_job.rt > quantum:
            cur_time += quantum
            next_job.rt -= quantum
        else:
            cur_time += next_job.rt
            rem_bt -= next_job.rt
            next_job.rt = 0
            next_job.ct = cur_time
            next_job.tat = next_job.ct - next_job.at
            next_job.wt = next_job.tat - next_job.bt
            print(next_job)

        for job in jobs:
            if job.rt > 0 and job.at <= cur_time and job not in queue and job != next_job:
                queue.append(job)

if __name__ == "__main__":
    jobs = [
        Job(0, 1, 3),
        Job(1, 1, 5),
        Job(2, 5, 3),
        Job(3, 5, 1),
        Job(4, 6, 2),
        Job(5, 7, 3)
    ]
    quantum = 2
    round_robin(jobs, quantum)