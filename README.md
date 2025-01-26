# RT-Scheduling
OS Final Project 🖥️

## Real-Time Scheduling Simulation 🚦

This project simulates real-time scheduling on a multi-core system using a variety of scheduling policies. The program reads tasks and resource configurations from `in.txt` and logs the scheduling progress into `out.txt`. Each subsystem uses a distinct scheduling strategy and outputs periodic snapshots to track the system state.

---

## **Subsystems Overview** 🛠️

### **Subsystem 1: Weighted Round-Robin (WRR)** 🎯
- **Key Features:**
  - *Three Ready Queues:* Tasks are distributed among three cores, with each core maintaining its own queue.
  - *Dynamic Priority Management:* Quantum values are assigned based on burst times and adjusted dynamically.
  - *Wait Queue:* Tasks that lack sufficient resources wait until conditions improve.  
  - *Snapshot:* Every iteration generates a snapshot, saved to `out.txt`.

---

### **Subsystem 2: Shortest Remaining Time First (SRTF)** ⏳
- **Key Features:**
  - *Two Ready Queues:* Each core picks the next task with the shortest remaining burst time.
  - *No Wait Queue:* Tasks must fit within available resources immediately; if not, they are delayed.
  - *Efficient Completion:* Reduces average waiting time by processing the smallest remaining job first.

---

### **Subsystem 3: Rate-Monotonic Scheduling (RMS)** 📊
- **Key Features:**
  - *Periodic Tasks:* Tasks come with defined periods, deadlines, and repetitions.
  - *Schedulability Testing:* Uses utilization bounds to check if the task set is schedulable.
  - *Resource Borrowing:* If schedulability cannot be achieved, extra resources are borrowed from other subsystems.
  - *Snapshot:* A snapshot is saved after each scheduling cycle.

---

### **Subsystem 4: First-Come, First-Served (FCFS)** 📋
- **Key Features:**
  - *Two Cores:* Tasks are processed in the order they arrive, with no preemption.
  - *Dependency Handling:* Tasks with dependencies will wait until all prerequisites are completed.
  - *Error Handling:* Tasks have a 30% chance of failing and re-entering the queue.
  - *Snapshot:* A snapshot is logged after each task is processed.

---

## **Project Structure** 🗂️
```
.
├── FUM_OS_1403-01_Project2.pdf
├── in.txt
├── main.py
├── out-format.txt
├── out.txt
├── README.md
├── ready_queues
│   ├── job_list1.json
│   ├── job_list.json
│   ├── ready_queue1.json
│   ├── ready_queue3.json
│   └── ready_queue4.json
├── resource_utils.py
├── subsystem1.py
├── subsystem2.py
├── subsystem3.py
├── subsystem4.py
├── wait_queue_log.txt
└── wait_queues
    └── wait_queue1.json

4 directories, 24 files
```


---

## **How to Run the Project** 🚀

1. **Install Python 3.11:**  
   If not already installed, download and install Python 3.11 from [python.org](https://www.python.org/downloads/).

2. **Prepare Input File:**  
   Make sure `in.txt` is formatted correctly with the necessary tasks and resource configurations.

3. **Run the Program:**  
   From the project root directory, run:
   ```bash
   python main.py

4. **Check the Output**:
    - **Snapshots**: Each subsystem’s state is logged to out.txt.
    Wait Queue Logs: Check wait_queue_log.txt for tasks that enter and exit the wait queue.

5. **Customize Subsystem Behavior**:
    To adjust scheduling policies or behavior, modify the corresponding subsystemX.py file.

## **Contributors** 🙌
- **Erfan Mahmoudi** 🧑‍💻
- **Seyed Alireza Hashemi** 👨‍💻

Enjoy exploring real-time scheduling in action! 🚀🎉
