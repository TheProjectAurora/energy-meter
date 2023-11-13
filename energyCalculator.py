import psutil
import time
import threading
import json


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

    def __init__(self, processor='i9-12900KS', ram='ddr4'):
        self.processor = processor
        self.ram = ram
        self.load_consumption_data()

        self.process = None
        self.running = False
        self.consumption_metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "network_io_initial": None,
            "network_io_final": None,
            "thread_start_time": time.time(),
            "thread_execution_time": 0
        }

    def load_consumption_data(self):
        try:
            with open('consumptions.json') as f:
                self.consumption_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading consumption data: {e}")
            self.consumption_data = {}

    def start_test(self, name, attributes):
        self.process = next((proc for proc in psutil.process_iter(['pid', 'name'])
                             if proc.info['name'].lower() == 'chrome'), None)
        if not self.process:
            print("Chromium process not found!")
            return

        self.running = True
        self.thread = threading.Thread(target=self.measure_consumption)
        self.thread.start()

    def end_test(self, name, attributes):
        if not self.process:
            return

        self.running = False
        self.thread.join()
        self.calculate_consumption()
        self.print_consumption_results()  # Call print results at the end of the test

    def measure_consumption(self):
        self.consumption_metrics["network_io_initial"] = psutil.net_io_counters()
        while self.running:
            self.record_cpu_consumption()
            self.record_memory_consumption()
            time.sleep(0.01)
        self.consumption_metrics["network_io_final"] = psutil.net_io_counters()

    def record_cpu_consumption(self):
        cpu_usage = self.process.cpu_percent(interval=0.1)
        self.consumption_metrics["cpu_usage"].append(cpu_usage)

    def record_memory_consumption(self):
        memory_usage = self.process.memory_info().rss / (1024 * 1024)  # Convert to MB
        self.consumption_metrics["memory_usage"].append(memory_usage)

    def calculate_consumption(self):
        self.consumption_metrics["thread_execution_time"] = time.time() - self.consumption_metrics["thread_start_time"]
        # Add more calculation logic if necessary

    def print_consumption_results(self):
        # Calculate average CPU and Memory consumption
        average_cpu_usage = sum(self.consumption_metrics["cpu_usage"]) / len(self.consumption_metrics["cpu_usage"]) if self.consumption_metrics["cpu_usage"] else 0
        average_memory_usage = sum(self.consumption_metrics["memory_usage"]) / len(self.consumption_metrics["memory_usage"]) if self.consumption_metrics["memory_usage"] else 0
        total_time = self.consumption_metrics["thread_execution_time"]
        
        # Calculate network usage
        bytes_sent = self.consumption_metrics["network_io_final"].bytes_sent - self.consumption_metrics["network_io_initial"].bytes_sent
        bytes_received = self.consumption_metrics["network_io_final"].bytes_recv - self.consumption_metrics["network_io_initial"].bytes_recv

        #calculate energy consumptions
        cpu_consumption = average_cpu_usage/100 * self.consumption_data['processor'][self.processor]* total_time
        memory_consumption = average_memory_usage * self.consumption_data['ram'][self.ram] * total_time
        network_consumption = (bytes_sent + bytes_received)/1024/1024 * self.consumption_data['network']
        total_consumption = cpu_consumption + memory_consumption + network_consumption

        # Print the results
        print("")
        print(color.CYAN + f"Energy Consumption Results: {total_consumption:.2f} Ws" + color.END)
        print("")
        print(f"Average CPU Consumption: {cpu_consumption:.2f} Ws")
        print(f"Average Memory Consumption: {memory_consumption:.2f} Ws")
        print(f"Average Network Consumption: {network_consumption:.2f} Ws")