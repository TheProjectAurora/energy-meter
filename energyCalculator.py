import psutil
import time
import threading
import json
import platform
import os
#import wmi

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class energyCalculator:    
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, ram='ddr4'):
        self.processor = self.get_cpu_info()
        self.ram = ram
        self.load_consumption_data()

        self.browser_process = None
        self.node_process = None
        self.running = False
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


    def load_consumption_data(self):
        try:
            with open('consumptions.json') as f:
                self.consumption_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading consumption data: {e}")
            self.consumption_data = {}

    def start_test(self, name, attributes):
        self.browser_process = next((proc for proc in psutil.process_iter(['pid', 'name'])
                             if proc.info['name'].lower() == 'chrome'), None)
        if not self.browser_process:
            print("Chromium process not found!")
            return
        
        self.node_process = next(proc for proc in psutil.process_iter(['pid', 'cmdline'])
                             if 'node' and 'index.js' in proc.info.get('cmdline', []))
        if not self.node_process:
            print("Node process not found!")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.measure_consumption)
        self.thread.start()

    def end_test(self, name, attributes):
        if not self.browser_process:
            return

        self.running = False
        self.thread.join()
        self.calculate_consumption()
        self.print_consumption_results()  # Call print results at the end of the test

    def measure_consumption(self):
        self.consumption_metrics["network_io_initial"] = psutil.net_io_counters() #pernic=True)['lo']
        while self.running:
            self.record_cpu_consumption()
            self.record_memory_consumption()
            time.sleep(0.01)
        self.consumption_metrics["network_io_final"] = psutil.net_io_counters() #pernic=True)['lo']


    def record_cpu_consumption(self):
        cpu_usage_browser = self.browser_process.cpu_percent(interval=0.1)
        cpu_usage_node = self.node_process.cpu_percent(interval=0.1)
        self.consumption_metrics["cpu_usage_browser"].append(cpu_usage_browser)
        self.consumption_metrics["cpu_usage_node"].append(cpu_usage_node)

    def record_memory_consumption(self):
        memory_usage_browser = self.browser_process.memory_info().rss / (1024 * 1024)  # Convert to MB
        memory_usage_node = self.node_process.memory_info().rss / (1024 * 1024)  # Convert to MB
        self.consumption_metrics["memory_usage_browser"].append(memory_usage_browser)
        self.consumption_metrics["memory_usage_node"].append(memory_usage_node)

    def calculate_consumption(self):
        self.consumption_metrics["thread_execution_time"] = time.time() - self.consumption_metrics["thread_start_time"]
        # Add more calculation logic if necessary

    def print_consumption_results(self):
        consumptions = self.get_consumption()

        # Print the results
        print("")
        print(color.CYAN + f"Energy Consumption Results: {consumptions['total_consumption']:.2f} Ws" + color.END)
        print("")
        print("Frontend")
        print(f"Browser CPU Consumption: {consumptions['browser_cpu_consumption']:.2f} Ws")
        print(f"Browser Memory Consumption: {consumptions['browser_memory_consumption']:.2f} Ws")
        print("")
        print("Backend")
        print(f"Node CPU Consumption: {consumptions['node_cpu_consumption']:.2f} Ws")
        print(f"Node Memory Consumption: {consumptions['node_memory_consumption']:.2f} Ws")
        print("")
        print(f"Network Consumption: {consumptions['network_consumption']:.2f} Ws")
        self.__init__()

    def get_consumption(self):
        # Calculate average CPU and Memory consumption
        average_cpu_usage_browser = sum(self.consumption_metrics["cpu_usage_browser"]) / len(self.consumption_metrics["cpu_usage_browser"]) if self.consumption_metrics["cpu_usage_browser"] else 0
        average_cpu_usage_node = sum(self.consumption_metrics["cpu_usage_node"]) / len(self.consumption_metrics["cpu_usage_node"]) if self.consumption_metrics["cpu_usage_node"] else 0
        average_memory_usage_browser = sum(self.consumption_metrics["memory_usage_browser"]) / len(self.consumption_metrics["memory_usage_browser"]) if self.consumption_metrics["memory_usage_browser"] else 0
        average_memory_usage_node = sum(self.consumption_metrics["memory_usage_node"]) / len(self.consumption_metrics["memory_usage_node"]) if self.consumption_metrics["memory_usage_node"] else 0
        total_time = self.consumption_metrics["thread_execution_time"]
        
        # Calculate network usage
        bytes_sent = self.consumption_metrics["network_io_final"].bytes_sent - self.consumption_metrics["network_io_initial"].bytes_sent
        bytes_received = self.consumption_metrics["network_io_final"].bytes_recv - self.consumption_metrics["network_io_initial"].bytes_recv

        #calculate energy consumptions
        try:
            self.consumption_data['processor'][self.processor]
        except KeyError:
            print("")
            print(f"Processor {self.processor} not found in consumption data. Using default value of 100 Ws. Add it to the consumption data to consumption.json to get more accurate results.")
            self.consumption_data['processor'][self.processor] = 100
    
        browser_cpu_consumption = average_cpu_usage_browser/100 * self.consumption_data['processor'][self.processor]* total_time
        node_cpu_consumption = average_cpu_usage_node/100 * self.consumption_data['processor'][self.processor]* total_time
        browser_memory_consumption = average_memory_usage_browser * self.consumption_data['ram'][self.ram] * total_time
        node_memory_consumption = average_memory_usage_node * self.consumption_data['ram'][self.ram] * total_time
        
        network_consumption = (bytes_sent + bytes_received)/1024/1024 * self.consumption_data['network']
        total_consumption = browser_cpu_consumption + node_cpu_consumption + browser_memory_consumption + node_memory_consumption + network_consumption
        
        consumptions = {
            "total_consumption": total_consumption,
            "browser_cpu_consumption": browser_cpu_consumption,
            "node_cpu_consumption": node_cpu_consumption,
            "browser_memory_consumption": browser_memory_consumption,
            "node_memory_consumption": node_memory_consumption,
            "network_consumption": network_consumption
        }
        return consumptions