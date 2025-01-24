class Job:
    def __init__(self, id ,name, burst_time, resource1, resource2, arrival_time, period, repetition, **kwargs):
        self.id = id
        self.name = name
        self.burst_time = burst_time
        self.resource1 = resource1
        self.resource2 = resource2
        self.arrival_time = arrival_time
        self.period = period
        self.repetition = repetition
        self.state = kwargs.get("state", "Ready") 
    def __str__(self):
        return f""" Job properties:
        {"id":^10} | {"name":^10} | {"burst time":^10} | {"resource1":^10} | {"resource2":^10} | {"arrival time":^12} | {"period":^10} | {"repetition":^10} | {"state":^10} |
        {self.id:^10} | {self.name:^10} | {self.burst_time:^10} | {self.resource1:^10} | {self.resource2:^10} | {self.arrival_time:^12} | {self.period:^10} | {self.repetition:^10} | {self.state:^10} |"""


def handle_subSystem2(resources, tasks):
    print("Handling Subsystem 2")
    print(tasks)
    print(resources)
    schedule = Rate_Monotonic(tasks)  # Shortest Remaining Time First

    print("Schedule:" + str(schedule))
    exit()
    pass

def Rate_Monotonic(tasks):
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
        name, burst_time, resource1, resource2, arrival_time, period, repetition = task.split()
        parsed_tasks.append({
            "name": name,
            "burst_time": int(burst_time),
            "resource1": int(resource1),
            "resource2": int(resource2),
            "arrival_time": int(arrival_time),
            "period": int(period),
            "repetition": int(repetition),
            "remaining_repetition": int(repetition),
            "next_deadline": int(arrival_time) + int(period),  # محاسبه ددلاین اولیه
        })

    # محاسبه بار کاری سیستم
    utilization = sum(task["burst_time"] / task["period"] for task in parsed_tasks)
    n = len(parsed_tasks)
    utilization_bound = n * (2 ** (1 / n) - 1)

    # بررسی قابلیت زمان‌بندی
    # if utilization > utilization_bound:
        # return False, []  # زمان‌بندی‌پذیر نیست

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

# def Rate_Monotonic1(tasks):
#     """
#     وظایف را براساس الگوریتم RMS زمان‌بندی می‌کند.
    
#     tasks: لیستی از رشته‌های وظایف به فرمت 'T31 20 2 3 50 10'.
#     خروجی:
#     - True و برنامه زمان‌بندی اگر قابل زمان‌بندی باشد.
#     - False و None اگر زمان‌بندی‌پذیر نباشد.
#     """
#     # پارس کردن اطلاعات وظایف
#     parsed_tasks = []
#     for task in tasks:
#         name, burst_time, resource1, resource2, period, repetition = task.split()
#         parsed_tasks.append({
#             "name": name,
#             "burst_time": int(burst_time),
#             "resource1": int(resource1),
#             "resource2": int(resource2),
#             "period": int(period),
#             "repetition": int(repetition),
#         })
    
#     # محاسبه بار کاری سیستم
#     utilization = sum(task["burst_time"] / task["period"] for task in parsed_tasks)
#     n = len(parsed_tasks)
#     utilization_bound = n * (2 ** (1 / n) - 1)
    
#     # بررسی قابلیت زمان‌بندی
#     if utilization > utilization_bound:
#         return False, None  # زمان‌بندی‌پذیر نیست

#     # ایجاد جدول زمان‌بندی
#     schedule = []
#     current_time = 0
#     total_tasks = sum(task["repetition"] for task in parsed_tasks)
    
#     while total_tasks > 0:
#         # یافتن وظیفه‌ای که باید اجرا شود
#         parsed_tasks.sort(key=lambda x: x["period"])  # اولویت براساس دوره تناوب
#         task_scheduled = False
        
#         for task in parsed_tasks:
#             if task["repetition"] > 0 and current_time % task["period"] == 0:
#                 # اجرای وظیفه
#                 execution_time = task["burst_time"]
#                 schedule.append((task["name"], execution_time))
#                 current_time += execution_time
#                 task["repetition"] -= 1
#                 task_scheduled = True
#                 total_tasks -= 1
#                 break
        
#         if not task_scheduled:
#             # وقتی وظیفه‌ای برای اجرا وجود ندارد
#             schedule.append(("-", 1))
#             current_time += 1
    
    
#     return True, schedule

# def Rate_Monotonic(tasks):
#     """
#     وظایف را براساس الگوریتم RMS زمان‌بندی می‌کند.
    
#     tasks: لیستی از رشته‌های وظایف به فرمت 'T31 20 2 3 0 50 10'.
#     خروجی:
#     - True و برنامه زمان‌بندی اگر قابل زمان‌بندی باشد.
#     - False و None اگر زمان‌بندی‌پذیر نباشد.
#     """
#     # پارس کردن اطلاعات وظایف
#     parsed_tasks = []
#     for task in tasks:
#         name, burst_time, resource1, resource2, arrival_time, period, repetition = task.split()
#         parsed_tasks.append({
#             "name": name,
#             "burst_time": int(burst_time),
#             "resource1": int(resource1),
#             "resource2": int(resource2),
#             "arrival_time": int(arrival_time),  # مقدار زمان ورود
#             "period": int(period),
#             "repetition": int(repetition),
#             "remaining_repetition": int(repetition),  # تعداد تکرار باقی‌مانده
#         })
    
#     # محاسبه بار کاری سیستم
#     utilization = sum(task["burst_time"] / task["period"] for task in parsed_tasks)
#     n = len(parsed_tasks)
#     utilization_bound = n * (2 ** (1 / n) - 1)
    
#     # بررسی قابلیت زمان‌بندی
#     if utilization > utilization_bound:
#         return False, None  # زمان‌بندی‌پذیر نیست

#     # ایجاد جدول زمان‌بندی
#     schedule = []

#     current_time = 0
#     total_tasks = sum(task["remaining_repetition"] for task in parsed_tasks)
    
#     while total_tasks > 0:
#         # یافتن وظیفه‌ای که باید اجرا شود
#         parsed_tasks.sort(key=lambda x: (x["period"], x["arrival_time"]))  # اولویت براساس دوره تناوب و زمان ورود
#         task_scheduled = False
        
#         for task in parsed_tasks:
#             if task["remaining_repetition"] > 0 and current_time >= task["arrival_time"]:
#                 # اجرای وظیفه
#                 execution_time = task["burst_time"]
#                 schedule.append((task["name"], execution_time))
#                 current_time += execution_time
#                 task["remaining_repetition"] -= 1
#                 task_scheduled = True
#                 total_tasks -= 1
#                 break
        
#         if not task_scheduled:
#             # وقتی وظیفه‌ای برای اجرا وجود ندارد
#             if schedule and schedule[-1][0] == '-':
#                 schedule[-1] = ('-', schedule[-1][1] + 1)
#             else:
#                 schedule.append(("-", 1))
#             current_time += 1
    
#     return True, schedule


# # def Rate_Monotonic(tasks):
#     """
#     وظایف را براساس الگوریتم RMS زمان‌بندی می‌کند.
    
#     tasks: لیستی از رشته‌های وظایف به فرمت 'T31 20 2 3 50 10'.
#     خروجی:
#     - True و برنامه زمان‌بندی اگر قابل زمان‌بندی باشد.
#     - False و None اگر زمان‌بندی‌پذیر نباشد.
#     """
#     # پارس کردن اطلاعات وظایف
#     parsed_tasks = []
#     for task in tasks:
#         name, burst_time, resource1, resource2, arrival_time, period, repetition = task.split()
#         parsed_tasks.append({
#             "name": name,
#             "burst_time": int(burst_time),
#             "resource1": int(resource1),
#             "resource2": int(resource2),
#             "arrival_time": int(arrival_time),  # مقدار زمان ورود
#             "period": int(period),
#             "repetition": int(repetition),
#         })

    
#     # محاسبه بار کاری سیستم
#     utilization = sum(task["burst_time"] / task["period"] for task in parsed_tasks)
#     n = len(parsed_tasks)
#     utilization_bound = n * (2 ** (1 / n) - 1)
    
#     # بررسی قابلیت زمان‌بندی
#     if utilization > utilization_bound:
#         return False, None  # زمان‌بندی‌پذیر نیست

#     # ایجاد جدول زمان‌بندی
#     schedule = []
#     current_time = 0
#     total_tasks = sum(task["repetition"] for task in parsed_tasks)
    
#     while total_tasks > 0:
#         # یافتن وظیفه‌ای که باید اجرا شود
#         parsed_tasks.sort(key=lambda x: x["period"])  # اولویت براساس دوره تناوب
#         task_scheduled = False
        
#         for task in parsed_tasks:
#             if task["repetition"] > 0 and current_time % task["period"] == 0:
#                 # اجرای وظیفه
#                 execution_time = task["burst_time"]
#                 schedule.append((task["name"], execution_time))
#                 current_time += execution_time
#                 task["repetition"] -= 1
#                 task_scheduled = True
#                 total_tasks -= 1
#                 break
        
#         if not task_scheduled:
#             # وقتی وظیفه‌ای برای اجرا وجود ندارد
#             if schedule and schedule[-1][0] == '-':
#                 schedule[-1] = ('-', schedule[-1][1] + 1)
#             else:
#                 schedule.append(("-", 1))
#             current_time += 1
    
#     return True, schedule
