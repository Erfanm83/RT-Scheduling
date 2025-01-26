import tkinter as tk
from tkinter import ttk, messagebox

# Process class to store process details
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None

# First Come First Serve (FCFS)
def fcfs(processes):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    for process in processes:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        process.start_time = current_time
        process.completion_time = current_time + process.burst_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        current_time = process.completion_time
    return processes

# Non-Preemptive Shortest Job First (SJF)
def non_preemptive_sjf(processes):
    processes.sort(key=lambda p: (p.arrival_time, p.burst_time))
    completed = []
    current_time = 0
    while processes:
        ready_queue = [p for p in processes if p.arrival_time <= current_time]
        if not ready_queue:
            current_time += 1
            continue
        shortest_job = min(ready_queue, key=lambda p: p.burst_time)
        processes.remove(shortest_job)
        shortest_job.start_time = current_time
        shortest_job.completion_time = current_time + shortest_job.burst_time
        shortest_job.turnaround_time = shortest_job.completion_time - shortest_job.arrival_time
        shortest_job.waiting_time = shortest_job.turnaround_time - shortest_job.burst_time
        current_time = shortest_job.completion_time
        completed.append(shortest_job)
    return completed

# Preemptive Shortest Job First (SJF)
def preemptive_sjf(processes):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    completed = []
    while processes:
        ready_queue = [p for p in processes if p.arrival_time <= current_time]
        if not ready_queue:
            current_time += 1
            continue
        shortest_job = min(ready_queue, key=lambda p: p.burst_time)
        if shortest_job.burst_time == 0:
            processes.remove(shortest_job)
            completed.append(shortest_job)
            continue
        shortest_job.start_time = current_time if shortest_job.start_time is None else shortest_job.start_time
        shortest_job.burst_time -= 1
        current_time += 1
        if shortest_job.burst_time == 0:
            shortest_job.completion_time = current_time
            shortest_job.turnaround_time = shortest_job.completion_time - shortest_job.arrival_time
            shortest_job.waiting_time = shortest_job.turnaround_time - shortest_job.burst_time
    return completed

# Round Robin (RR)
def round_robin(processes, quantum):
    queue = processes[:]
    current_time = 0
    while queue:
        process = queue.pop(0)
        if process.arrival_time > current_time:
            current_time = process.arrival_time
        execution_time = min(process.burst_time, quantum)
        process.start_time = current_time if process.start_time is None else process.start_time
        process.burst_time -= execution_time
        current_time += execution_time
        if process.burst_time > 0:
            queue.append(process)
        else:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
    return processes

# Priority Scheduling
def priority_scheduling(processes):
    processes.sort(key=lambda p: (p.arrival_time, p.priority))
    current_time = 0
    completed = []
    while processes:
        ready_queue = [p for p in processes if p.arrival_time <= current_time]
        if not ready_queue:
            current_time += 1
            continue
        highest_priority = min(ready_queue, key=lambda p: p.priority)
        processes.remove(highest_priority)
        highest_priority.start_time = current_time
        highest_priority.completion_time = current_time + highest_priority.burst_time
        highest_priority.turnaround_time = highest_priority.completion_time - highest_priority.arrival_time
        highest_priority.waiting_time = highest_priority.turnaround_time - highest_priority.burst_time
        current_time = highest_priority.completion_time
        completed.append(highest_priority)
    return completed

# GUI implementation
def create_gui():
    def add_process():
        try:
            pid = int(pid_entry.get())
            arrival_time = int(arrival_time_entry.get())
            burst_time = int(burst_time_entry.get())
            priority = int(priority_entry.get()) if priority_entry.get() else None
            processes.append(Process(pid, arrival_time, burst_time, priority))
            messagebox.showinfo("Success", "Process added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

    def simulate_algorithm():
        if algorithm_combobox.get() == "FCFS":
            scheduled_processes = fcfs(processes)
        elif algorithm_combobox.get() == "Non-Preemptive SJF":
            scheduled_processes = non_preemptive_sjf(processes)
        elif algorithm_combobox.get() == "Preemptive SJF":
            scheduled_processes = preemptive_sjf(processes)
        elif algorithm_combobox.get() == "Round Robin":
            quantum = int(quantum_entry.get())
            scheduled_processes = round_robin(processes, quantum)
        elif algorithm_combobox.get() == "Priority Scheduling":
            scheduled_processes = priority_scheduling(processes)
        else:
            messagebox.showerror("Error", "Select a valid algorithm.")
            return

        result_text.delete("1.0", tk.END)
        for process in scheduled_processes:
            result_text.insert(tk.END, f"P{process.pid}: Start: {process.start_time}, Completion: {process.completion_time}, TAT: {process.turnaround_time}, WT: {process.waiting_time}\n")

    # Main window
    root = tk.Tk()
    root.title("CPU Scheduling Simulator")

    tk.Label(root, text="Process ID:").grid(row=0, column=0)
    pid_entry = tk.Entry(root)
    pid_entry.grid(row=0, column=1)

    tk.Label(root, text="Arrival Time:").grid(row=1, column=0)
    arrival_time_entry = tk.Entry(root)
    arrival_time_entry.grid(row=1, column=1)

    tk.Label(root, text="Burst Time:").grid(row=2, column=0)
    burst_time_entry = tk.Entry(root)
    burst_time_entry.grid(row=2, column=1)

    tk.Label(root, text="Priority:").grid(row=3, column=0)
    priority_entry = tk.Entry(root)
    priority_entry.grid(row=3, column=1)

    tk.Button(root, text="Add Process", command=add_process).grid(row=4, column=0, columnspan=2)

    tk.Label(root, text="Algorithm:").grid(row=5, column=0)
    algorithm_combobox = ttk.Combobox(root, values=["FCFS", "Non-Preemptive SJF", "Preemptive SJF", "Round Robin", "Priority Scheduling"])
    algorithm_combobox.grid(row=5, column=1)

    tk.Label(root, text="Quantum (for RR):").grid(row=6, column=0)
    quantum_entry = tk.Entry(root)
    quantum_entry.grid(row=6, column=1)

    tk.Button(root, text="Simulate", command=simulate_algorithm).grid(row=7, column=0, columnspan=2)

    result_text = tk.Text(root, height=10, width=50)
    result_text.grid(row=8, column=0, columnspan=2)

    root.mainloop()

processes = []
create_gui()