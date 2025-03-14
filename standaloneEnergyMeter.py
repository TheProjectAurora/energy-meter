import psutil
import time
import json
import platform
import os
import argparse
import logging
from pathlib import Path

if platform.system() == "Windows":
    import wmi

###############################################################################
# Logging
###############################################################################
logging.basicConfig(
    level=logging.DEBUG,  # for maximum verbosity
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("energyMeter")

###############################################################################
# Color setup
###############################################################################
class color:
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

###############################################################################
# Detecting surrounds
###############################################################################
logger.debug(f"Processor: {platform.processor()}")
logger.debug(f"Machine: {platform.machine()}")
logger.debug(f"System: {platform.system()}")
logger.debug(f"Version: {platform.version()}")
logger.debug(f"Release: {platform.release()}")
logger.debug(f"Node: {platform.node()}")
logger.debug(f"Platform: {platform.platform()}")
logger.debug(f"CPU Count: {psutil.cpu_count(logical=False)}")
logger.debug(f"Logical CPU Count: {psutil.cpu_count(logical=True)}")
logger.debug(f"RAM: {psutil.virtual_memory().total / (1024 * 1024 * 1024):.2f} GB")  # in GB

class energyMeter(object):
    """
    A class that calculates energy consumption during a test.
    """
    def __init__(self, pid, ram="ddr4"):
        logger.debug("Entering energyMeter.__init__")
        self.config = None
        self.platform_id = platform.system()
        self.processor = self.get_cpu_info()
        self.process = psutil.Process(pid)
        self.ram = ram
        self.load_configs()

        self.running = False
        self.reset_consumption_metrics()

    def load_configs(self):
        logger.debug("Entering energyMeter.load_configs")
        config_file = Path(__file__).resolve().parent / "energyMeterConfig.json"
        try:
            logger.debug(f"Loading configs from {config_file}")
            self.config = json.loads(config_file.read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.info(f"Error loading configs from {config_file}: {e}")
            self.config = {
                "processor": {
                    "DEFAULT": 100.0,
                },
                "ram": {"ddr4": 0.0000375},
                "network": 1.8,
            }

        if self.processor not in self.config["processor"]:
            self.config["processor"][self.processor] = self.config["processor"]["DEFAULT"]

    def get_cpu_info(self):
        logger.debug("Entering energyMeter.get_cpu_info")
        try:
            if self.platform_id == "Windows":
                c = wmi.WMI()
                cpus = [cpu.Name.strip() for cpu in c.Win32_Processor()]
                return ", ".join(cpus) if cpus else "Unknown CPU"
            elif self.platform_id == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            logger.debug(f"Detected CPU model: {line}")
                            processor = line.split(":")[1].strip()
                            if "@" in processor:
                                at_position = processor.find("@")
                                processor_strip = processor[: at_position - 1].strip()
                                logger.debug(f"Detected @ in CPU model: {processor_strip}")
                                return processor_strip
                            else:
                                return processor
                return "Unknown CPU"
            elif self.platform_id == "Darwin":
                return os.popen("sysctl -n machdep.cpu.brand_string").read().strip()
            else:
                return "Unknown Operating System"
        except Exception:
            return "Unknown Operating System"

    def reset_consumption_metrics(self):
        logger.debug("Entering energyMeter.reset_consumption_metrics")
        self.consumption_metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "network_io_initial": None,
            "network_io_final": None,
            "thread_start_time": time.time(),
            "thread_execution_time": 0,
        }

    def measure_consumption(self, duration=None, interval=1.0):
        """
        Measure consumption for a given duration (in seconds).
        If duration is None, run until self.running is set to False externally.
        """
        logger.debug("Entering energyMeter.measure_consumption")
        self.consumption_metrics["network_io_initial"] = self.get_localhostmetrics()
        start_time = time.time()
        while self.running:
            self.record_consumption_metrics()
            if duration and (time.time() - start_time) >= duration:
                self.running = False
            time.sleep(interval)
        self.consumption_metrics["network_io_final"] = self.get_localhostmetrics()

    def get_localhostmetrics(self):
        logger.debug("Entering energyMeter.get_localhostmetrics")
        interfaces = psutil.net_io_counters(pernic=True)
        for interface_name in interfaces:
            if interface_name.lower().startswith("lo"):
                logger.debug(f"Found localhost interface: {interface_name}")
                return interfaces[interface_name]

    def record_consumption_metrics(self):
        logger.debug("Entering energyMeter.record_consumption_metrics")
        self.record_total_consumption(self.process)

    def record_total_consumption(self, process):
        logger.debug(f"Entering energyMeter.record_total_consumption for process {process.pid}")
        self.record_memory_consumption(process)
        self.record_cpu_consumption(process)

    def record_cpu_consumption(self, process):
        logger.debug("Entering energyMeter.record_cpu_consumption")
        try:
            cpu_usage = process.cpu_percent(interval=1.0)
            self.consumption_metrics["cpu_usage"].append(cpu_usage)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    def record_memory_consumption(self, process):
        logger.debug("Entering energyMeter.record_memory_consumption")
        try:
            memory_usage = process.memory_info().rss / (1024 * 1024)
            self.consumption_metrics["memory_usage"].append(memory_usage)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    def calculate_consumption(self):
        logger.debug("Entering energyMeter.calculate_consumption")
        self.running = False
        self.consumption_metrics["thread_execution_time"] = time.time() - self.consumption_metrics["thread_start_time"]

    def print_consumption_results(self):
        logger.debug("Entering energyMeter.print_consumption_results")
        consumptions = self.get_consumption()

        print("")
        print(color.CYAN + f"🌱 Energy Consumption Results: {consumptions['total_consumption']:.2f} Ws 🌱" + color.END)
        print("")
        print(f"💻 CPU Consumption: {consumptions['cpu_consumption']:.2f} Ws")
        print(f"💭 Memory Consumption: {consumptions['memory_consumption']:.2f} Ws")
        print("")
        print(f"🌍 Network Consumption: {consumptions['network_consumption']:.2f} Ws")

    def get_consumption(self):
        logger.debug("Entering energyMeter.get_consumption")
        consumptions = {}
        consumptions["cpu_consumption"] = self.consumption("cpu_usage")
        consumptions["memory_consumption"] = self.consumption("memory_usage")
        consumptions["network_consumption"] = self.get_network_consumption()
        consumptions["total_consumption"] = (
            consumptions["cpu_consumption"]
            + consumptions["memory_consumption"]
            + consumptions["network_consumption"]
        )
        return consumptions

    def consumption(self, usage_type):
        logger.debug("Entering energyMeter.consumption")
        if usage_type == "cpu_usage":
            try:
                processor_consumption = self.config["processor"][self.processor]
            except KeyError:
                logger.info(
                    f"\nProcessor '{self.processor}' not found. Using default value of {self.config['processor']['DEFAULT']} Ws."
                )
                processor_consumption = self.config["processor"]["DEFAULT"]
            return (
                self.get_average_usage(usage_type)
                / 100
                * processor_consumption
                * self.consumption_metrics["thread_execution_time"]
            )
        elif usage_type == "memory_usage":
            return (
                self.get_average_usage(usage_type)
                * self.config["ram"][self.ram]
                * self.consumption_metrics["thread_execution_time"]
            )

    def get_average_usage(self, usage_type):
        logger.debug("Entering energyMeter.get_average_usage")
        usage = self.consumption_metrics[usage_type]
        return sum(usage) / len(usage) if usage else 0

    def get_network_consumption(self):
        logger.debug("Entering energyMeter.get_network_consumption")
        bytes_sent = (
            self.consumption_metrics["network_io_final"].bytes_sent - self.consumption_metrics["network_io_initial"].bytes_sent
        )
        bytes_received = (
            self.consumption_metrics["network_io_final"].bytes_recv - self.consumption_metrics["network_io_initial"].bytes_recv
        )
        return (bytes_sent + bytes_received) / 1024 / 1024 * self.config["network"]

def main():
    parser = argparse.ArgumentParser(description="Energy Meter")
    parser.add_argument("--pid", type=int, required=True, help="Process ID to monitor")
    # New parameters for measurement timing:
    parser.add_argument("--duration", type=int, default=10, help="Measurement duration in seconds")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between measurements in seconds")
    args = parser.parse_args()

    meter = energyMeter(pid=args.pid)
    meter.running = True
    # Pass duration and interval to measure_consumption
    meter.measure_consumption(duration=args.duration, interval=args.interval)
    meter.calculate_consumption()
    meter.print_consumption_results()

if __name__ == "__main__":
    main()
