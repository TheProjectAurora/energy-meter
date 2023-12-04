import psutil
import time
import threading
import json
import platform
import os
if platform.system() == 'Windows':
    import wmi

class color:
   CYAN = '\033[96m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class energyMeter(object): 
    """
    A class that calculates energy consumption during a test.

   
    """  
    ROBOT_LISTENER_API_VERSION = 3
    DEFAULT_PROCESSOR_CONSUMPTION = 100  # Watts

    def __init__(self, ram='ddr4'):
        self.processor = self.get_cpu_info()
        self.browser_process = None
        self.node_process = None
        self.ram = ram
        self.load_consumption_data()
        self.running = False
        self.reset_consumption_metrics()

    def load_consumption_data(self):
        try:
            with open('consumptions.json') as f:
                self.consumption_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading consumption data: {e}")
            self.consumption_data = {}
    
    def find_process(self, process_name, command=None):
        """
        Find a process by name. If a command is specified, it will be used for additional filtering.
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    if command:
                        if command in proc.info.get('cmdline', []):
                            return proc
                    else:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Process has terminated or cannot be accessed
        print(f"{process_name} process not found!")
        return None

    def get_cpu_info(self):
        try:
            # Check for Windows
            if platform.system() == "Windows":
                c = wmi.WMI()
                cpus = [cpu.Name.strip() for cpu in c.Win32_Processor()]
                return ', '.join(cpus) if cpus else "Unknown"

            # Check for Linux
            elif platform.system() == "Linux":
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
                return "Unknown"

            # Check for macOS
            elif platform.system() == "Darwin":
                return os.popen("sysctl -n machdep.cpu.brand_string").read().strip()

            else:
                return "Unknown Operating System"

        except Exception as e:
            return str(e)

    def start_test(self, name, attributes):
        self.reset_consumption_metrics()
        self.ensure_process_are_started()
        self.running = True
        self.thread = threading.Thread(target=self.measure_consumption)
        self.thread.start()
    
    def ensure_process_are_started(self):
        if not self.browser_process:
            self.browser_process = self.find_process('chrome')
        if not self.node_process:
            self.node_process = self.find_process('node', 'index.js')

    def reset_consumption_metrics(self):
        # Reset or initialize metrics
        self.consumption_metrics = {
            "cpu_usage_browser": [],
            "cpu_usage_node": [],
            "memory_usage_browser": [],
            "memory_usage_node": [],
            "network_io_initial": None,
            "network_io_final": None,
            "thread_start_time": time.time(),
            "thread_execution_time": 0
        }     

    def end_test(self, name, attributes):
        self.running = False
        self.thread.join()
        self.calculate_consumption()
        self.print_consumption_results()  # Call print results at the end of the test

    def measure_consumption(self):
        self.consumption_metrics["network_io_initial"] = psutil.net_io_counters(pernic=True)['lo']
        while self.running:
            self.record_consumption_metrics()
            time.sleep(0.01)
        self.consumption_metrics["network_io_final"] = psutil.net_io_counters(pernic=True)['lo']

    def record_consumption_metrics(self):
        self.record_total_consumption(self.browser_process, "browser")
        self.record_total_consumption(self.node_process, "node")

    def record_total_consumption(self, process, process_name):
        self.record_memory_consumption(process, process_name)
        self.record_cpu_consumption(process, process_name)

    def record_cpu_consumption(self, process, process_name):
        cpu_usage = process.cpu_percent(interval=0.1)
        self.consumption_metrics[f"cpu_usage_{process_name}"].append(cpu_usage)
    
    def record_memory_consumption(self, process, process_name):
        memory_usage = process.memory_info().rss / (1024 * 1024)
        self.consumption_metrics[f"memory_usage_{process_name}"].append(memory_usage)

    def calculate_consumption(self):
        self.consumption_metrics["thread_execution_time"] = time.time() - self.consumption_metrics["thread_start_time"]

    def print_consumption_results(self):
        consumptions = self.get_consumption()

        # Print the results
        print("")
        print(color.CYAN + f"🌱 Energy Consumption Results: {consumptions['total_consumption']:.2f} Ws 🌱" + color.END)
        print("")
        print("Frontend")
        print(f"💻 Browser CPU Consumption: {consumptions['browser_cpu_consumption']:.2f} Ws")
        print(f"💭 Browser Memory Consumption: {consumptions['browser_memory_consumption']:.2f} Ws")
        print("")
        print("Backend")
        print(f"💻 Node CPU Consumption: {consumptions['node_cpu_consumption']:.2f} Ws")
        print(f"💭 Node Memory Consumption: {consumptions['node_memory_consumption']:.2f} Ws")
        print("")
        print(f"🌍 Network Consumption: {consumptions['network_consumption']:.2f} Ws")

    def get_consumption(self):
        # Calculate average CPU and Memory consumption
        consumptions = {}
        
        consumptions["browser_cpu_consumption"] =  self.consumption('browser', 'cpu_usage')
        consumptions["node_cpu_consumption"] = self.consumption('node', 'cpu_usage')
        consumptions["browser_memory_consumption"] = self.consumption('browser', 'memory_usage')
        consumptions["node_memory_consumption"] = self.consumption('node', 'memory_usage')
        consumptions['network_consumption'] = self.get_network_consumption()
        consumptions['total_consumption'] =  consumptions["browser_cpu_consumption"] + consumptions["node_cpu_consumption"] + consumptions["browser_memory_consumption"] + consumptions["node_memory_consumption"] + consumptions['network_consumption']
        
        return consumptions
    
    def consumption(self, process_name, usage_type):
        if usage_type == 'cpu_usage':
                    #calculate energy consumptions
            try:
                processor_consumption = self.consumption_data['processor'][self.processor]
            except KeyError:
                print(f"\nProcessor {self.processor} not found. Using default value of {self.DEFAULT_PROCESSOR_CONSUMPTION} Ws.")
                processor_consumption = self.DEFAULT_PROCESSOR_CONSUMPTION
            return self.get_average_usage(process_name, usage_type)/100 * processor_consumption * self.consumption_metrics["thread_execution_time"]
            

        elif usage_type == 'memory_usage':
            return self.get_average_usage(process_name, usage_type) * self.consumption_data['ram'][self.ram] * self.consumption_metrics["thread_execution_time"]
    
    def get_average_usage(self, process_name, usage_type):
        usage = self.consumption_metrics[f"{usage_type}_{process_name}"]
        return sum(usage) / len(usage) if usage else 0
    
    def get_network_consumption(self):
        bytes_sent = self.consumption_metrics["network_io_final"].bytes_sent - self.consumption_metrics["network_io_initial"].bytes_sent
        bytes_received = self.consumption_metrics["network_io_final"].bytes_recv - self.consumption_metrics["network_io_initial"].bytes_recv
        return (bytes_sent + bytes_received)/1024/1024 * self.consumption_data['network']