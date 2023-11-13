import psutil
import time
import threading
import json

class energyCalculator(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, processor='i7-8650U', ram='ddr4'):
        self.process = None
        self.running = False
        self.processor = processor
        self.ram = ram 
        self.thread_start_time = 0
        self.cpu_usage_sum = 0
        self.cpu_usage_count = 0
        self.cpu_usage_list = []
        self.thread_start_time = time.time()
        self.memory_usage = 0
        self.memory_usage_sum = 0
        self.memory_usage_count = 0
        self.memory_usage_list = []
        self.network_cosummption_per_MB = 1.76

        with open('consumptions.json') as f:
            self.data = json.load(f)

    def _measure_consumption(self):
        self.process.cpu_percent(interval=None)
        self.initial_net_io = psutil.net_io_counters()
        while self.running:
            self._cpu_consumption()
            self._memory_consumption()
            time.sleep(0.01)
        self.final_net_io = psutil.net_io_counters()

    def _cpu_consumption(self):
        cpu_usage = self.process.cpu_percent(interval=0.1)
        self.cpu_usage_list.append(cpu_usage)
        self.cpu_usage_sum += cpu_usage
        self.cpu_usage_count += 1

    def _memory_consumption(self):
        memory_usage = self.process.memory_info().rss
        self.memory_usage_list.append(memory_usage)
        self.memory_usage_sum += memory_usage
        self.memory_usage_count += 1

    def _network_consumption(self):
        memory_usage = self.process.memory_info().rss
        self.memory_usage_list.append(memory_usage)
        self.memory_usage_sum += memory_usage
        self.memory_usage_count += 1

    def start_test(self, name, attributes):
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' == proc.info['name'].lower():
                self.process = psutil.Process(proc.info['pid'])
                break
        if not self.process:
            print("Chromium-prosessia ei löytynyt!")
            return
        self.running = True
        self.thread = threading.Thread(target=self._measure_consumption)
        self.thread.start()

    def end_test(self, name, attributes):
        if not self.process:
            return
        self.running = False
        self.thread.join()
        self.thread_execution_time = time.time() - self.thread_start_time
        average_cpu_consumption_Ws = self._cpu_e_consumption()
        average_memory_consumption_Ws = self._memory_e_consumption()
        network_consumption_W = self._network_e_consumption()

        print("")
        print(f"Ajon kokonaiskulutus Ws: {average_cpu_consumption_Ws + average_memory_consumption_Ws + network_consumption_W :.2f} Ws")
        print("")
        print(f"CPU-kuorman kulutus(Ws): {average_cpu_consumption_Ws:.2f} Ws")
        print(f"Muistikuorman kulutus(Ws): {average_memory_consumption_Ws:.2f} Ws")
        print(f"Verkkokuorma (Ws): {network_consumption_W:.2f} Ws")

    def _cpu_e_consumption(self):
        average_cpu_usage = self.cpu_usage_sum / self.cpu_usage_count if self.cpu_usage_count else 0
        average_cpu_consumption_Ws = (average_cpu_usage/100) * self.data['processor'][self.processor] * self.thread_execution_time
        return average_cpu_consumption_Ws

    def _memory_e_consumption(self):
        average_memory_usage = (self.memory_usage_sum/1024/1024) / self.memory_usage_count if self.memory_usage_count else 0
        average_memory_consumption_W = average_memory_usage * self.data['ram']['ddr4']
        average_memory_consumption_Ws = average_memory_consumption_W * self.thread_execution_time
        return average_memory_consumption_Ws

    def _network_e_consumption(self):
        bytes_sent = self.final_net_io.bytes_sent - self.initial_net_io.bytes_sent
        bytes_received = self.final_net_io.bytes_recv - self.initial_net_io.bytes_recv
        bytes_sum = bytes_sent + bytes_received
        network_consumption_W = bytes_sum/1024/1024 * self.network_cosummption_per_MB
        return network_consumption_W