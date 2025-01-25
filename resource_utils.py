import threading

# Shared resource pool, initialized here and updated through functions
resource_pool = {}

def initialize_resource_pool_from_file(file_path="in.txt"):
    """
    Reads the resource definitions from a file and initializes the global resource pool.
    The file should contain one line per subsystem, each with two integers representing r1 and r2.
    """
    global resource_pool
    resource_pool.clear()

    try:
        with open(file_path, 'r') as f:
            for i in range(4):
                line = f.readline().strip()
                # Parse resources for each subsystem
                r1, r2 = map(int, line.split(' '))
                subsystem_name = f'sub{i + 1}'
                resource_pool[subsystem_name] = {
                    'r1': r1,
                    'r2': r2,
                    'lock': threading.Lock()
                }
    except FileNotFoundError:
        print(f"Resource file {file_path} not found. Please ensure it exists.")
        raise
    except ValueError as ve:
        print("Error parsing the resource file. Ensure each line contains two integers separated by a space.")
        raise ve

def take_resources(requesting_subsystem, r1_needed, r2_needed):
    """
    Borrow resources from other subsystems.

    Args:
        requesting_subsystem: The name of the subsystem requesting resources (e.g., 'sub1').
        r1_needed: The amount of r1 resources needed.
        r2_needed: The amount of r2 resources needed.

    Returns:
        A tuple (borrowed_r1, borrowed_r2) indicating the amounts borrowed.
    """
    global resource_pool
    borrowed_r1 = 0
    borrowed_r2 = 0

    for subsystem, data in resource_pool.items():
        if subsystem == requesting_subsystem:
            continue  # Skip the requesting subsystem itself

        with data['lock']:
            # Check and take available resources
            if r1_needed > 0 and data['r1'] > 0:
                borrow_r1 = min(r1_needed, data['r1'])
                data['r1'] -= borrow_r1
                borrowed_r1 += borrow_r1
                r1_needed -= borrow_r1
            
            if r2_needed > 0 and data['r2'] > 0:
                borrow_r2 = min(r2_needed, data['r2'])
                data['r2'] -= borrow_r2
                borrowed_r2 += borrow_r2
                r2_needed -= borrow_r2

            if r1_needed <= 0 and r2_needed <= 0:
                break  # Stop if we've borrowed enough

    return borrowed_r1, borrowed_r2

def return_resources(requesting_subsystem, r1_returned, r2_returned):
    """
    Return borrowed resources to their original subsystems.

    Args:
        requesting_subsystem: The name of the subsystem returning resources (e.g., 'sub1').
        r1_returned: The amount of r1 resources to return.
        r2_returned: The amount of r2 resources to return.
    """
    global resource_pool
    for subsystem, data in resource_pool.items():
        if subsystem == requesting_subsystem:
            continue

        with data['lock']:
            # Simply return all remaining resources
            data['r1'] += r1_returned
            data['r2'] += r2_returned
            r1_returned = 0
            r2_returned = 0

        if r1_returned <= 0 and r2_returned <= 0:
            break

def check_valid_input(allsubSystemTasks, allsubSystemResources):
    """
    Validates that all tasks can be executed given the available resources.

    Args:
        allsubSystemTasks: A list of lists, where each inner list represents tasks for a subsystem.
        allsubSystemResources: A list of (r1, r2) tuples representing the resources available to each subsystem.
    """
    subsystemIndex = 1
    for subsystemTask in allsubSystemTasks:
        if subsystemIndex == 3:
            # For subsystem 3, check against the sum of all resources
            sumr1 = sum(resource[0] for resource in allsubSystemResources)
            sumr2 = sum(resource[1] for resource in allsubSystemResources)
            for t in subsystemTask:
                taskList = t.split(' ')
                r1 = int(taskList[2])
                r2 = int(taskList[3])
                if r1 > sumr1 or r2 > sumr2:
                    print(f"""
                    Error: Task requires more resources than available.
                    In Subsystem {subsystemIndex} 
                    {t[0:3]} Requested: r1: {r1} and r2: {r2}
                    Available Resources are r1: {sumr1} and r2: {sumr2}.
                    Exiting from program........
                    Try again later.
                    """)
                    exit(1)
        else:
            # For other subsystems, check against individual subsystem resources
            for t in subsystemTask:
                taskList = t.split(' ')
                r1 = int(taskList[2])
                r2 = int(taskList[3])
                availableR1 = allsubSystemResources[subsystemIndex - 1][0]
                availableR2 = allsubSystemResources[subsystemIndex - 1][1]
                if r1 > availableR1 or r2 > availableR2:
                    print(f"""
                    Error: Task requires more resources than available.
                    In Subsystem {subsystemIndex} 
                    {t[0:3]} Requested: r1: {r1} and r2: {r2}
                    Available Resources are r1: {availableR1} and r2: {availableR2}.
                    Exiting from program........
                    Try again later.
                    """)
                    exit(1)
        subsystemIndex += 1
