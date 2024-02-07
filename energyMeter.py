import psutil
import time
import threading
import json
import platform
import os
from pathlib import Path

if platform.system() == "Windows":
    import wmi

try:
    from mdgen import MDGen
except ModuleNotFoundError:
    MDGen = None

try:
    from Browser import __file__ as _BrowserBasePath
except ModuleNotFoundError:
    _BrowserBasePath = None


class color:
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class energyMeter(object):
    """
    A class that calculates energy consumption during a test.


    """

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, ram="ddr4"):
        self.config = None
        self.platform_id = platform.system()
        self.processor = self.get_cpu_info()
        self.browser_processes = None
        self.node_process = None
        self.tomcat_process = None
        self.ram = ram
        self.load_configs()

        self.running = False
        self.reset_consumption_metrics()
        self.summary = None
        self._output = os.environ.get("GITHUB_STEP_SUMMARY", None)
        if self._output and MDGen:
            self.summary = MDGen()
            self._output = Path(self._output)
            self._output.unlink(missing_ok=True)

    def load_configs(self):
        config_file = Path(__file__).resolve().parent / "energyMeterConfig.json"
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configs from {config_file}: {e}")
            self.config = {
                "processor": {
                    "DEFAULT": 100.0,
                },
                "ram": {"ddr4": 0.0000375},
                "network": 1.8,
            }

        if self.processor not in self.config["processor"]:
            self.config["processor"][self.processor] = self.config["processor"]["DEFAULT"]

    def find_process(self, process_name, command=None, expected_path=None):
        """
        Find a process by name. If a command is specified, it will be used for additional filtering.
        """

        def ensure_parent(process, pname):
            old = process
            try:
                found = False
                while not found:
                    current = old
                    parent = current.parent()
                    # For some reason, sometimes parent does not have info
                    try:
                        found = not parent.info["name"].lower().startswith(pname.lower())
                    except AttributeError:
                        found = True
                    old = parent

                return current
            except psutil.NoSuchProcess:
                return process

        windows_chrome_hack = []
        if process_name == "chrome":
            process_name = {
                "Linux": "chrome",
                "Windows": "chrome.exe",
                "Darwin": "Chromium",
            }[self.platform_id]

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if process_name.lower() in proc.info["name"].lower():
                    # if expected_path is defined, we'll check the path of the process to
                    # start with provided prefix to scope the to project. Check
                    # defaults to True to ignore the test *if* expected_path was not
                    # provided.
                    in_expected_path = True
                    executable_path = None
                    if expected_path:
                        executable_path = str(Path(proc.exe()).parent)
                        in_expected_path = executable_path.startswith(expected_path)

                    if in_expected_path:
                        if command:
                            if command in proc.info.get("cmdline", []):
                                if self.platform_id == "Windows":
                                    windows_chrome_hack.append(proc)
                                else:
                                    parent_process = ensure_parent(proc, process_name)
                                    return [parent_process, *parent_process.children()]
                        else:
                            print(f"{process_name} process found!")
                            if self.platform_id == "Windows":
                                windows_chrome_hack.append(proc)
                            else:
                                parent_process = ensure_parent(proc, process_name)
                                return [parent_process, *parent_process.children()]
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Process has terminated or cannot be accessed
        if self.platform_id == "Windows":
            if len(windows_chrome_hack) == 0:
                print(f"{process_name} process not found!")
                return None

            return windows_chrome_hack

        print(f"{process_name} process not found!")
        return None

    def get_cpu_info(self):
        try:
            # Check for Windows
            if self.platform_id == "Windows":
                c = wmi.WMI()
                cpus = [cpu.Name.strip() for cpu in c.Win32_Processor()]
                return ", ".join(cpus) if cpus else "Unknown"

            # Check for Linux
            elif self.platform_id == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            processor = line.split(":")[1].strip()
                            if "@" in processor:
                                # Find the position of "@" in the string
                                at_position = processor.find("@")

                                # Use slicing to extract the desired portion of the string
                                processor_strip = processor[
                                    : at_position - 1
                                ].strip()  # Subtract 1 to include the space before "@"
                                return processor_strip
                            else:
                                return processor
                return "Unknown"

            # Check for macOS
            elif self.platform_id == "Darwin":
                return os.popen("sysctl -n machdep.cpu.brand_string").read().strip()

            else:
                return "Unknown Operating System"

        except Exception:
            return "Unknown Operating System"

    def start_test(self, name, attributes):
        self.reset_consumption_metrics()
        self.ensure_process_are_started()

        self.running = True
        self.thread = threading.Thread(target=self.measure_consumption)
        self.thread.start()

    def ensure_process_are_started(self):

        # For now, if we are running inside venv and assume that rfbrowser will install
        # browser into inside venv, we only look for chrome that is inside.
        expected_chrome_path_prefix = None

        if _BrowserBasePath:
            expected_chrome_path_prefix = str(
                Path(_BrowserBasePath).parent / "wrapper" / "node_modules" / "playwright-core" / ".local-browsers"
            )

        if not self.browser_processes:
            self.browser_processes = self.find_process("chrome", expected_path=expected_chrome_path_prefix)
        if not self.node_process:
            self.node_process = self.find_process("node", "index.js")
        if not self.tomcat_process:
            self.tomcat_process = self.find_process("java", "org.apache.catalina.startup.Bootstrap")

    def reset_consumption_metrics(self):
        # Reset or initialize metrics
        self.consumption_metrics = {
            "cpu_usage_browser": [],
            "cpu_usage_node": [],
            "cpu_usage_tomcat": [],
            "memory_usage_browser": [],
            "memory_usage_node": [],
            "memory_usage_tomcat": [],
            "network_io_initial": None,
            "network_io_final": None,
            "thread_start_time": time.time(),
            "thread_execution_time": 0,
        }

    def end_test(self, name, attributes):
        self.running = False
        self.thread.join()
        self.calculate_consumption()
        self.print_consumption_results(name.name)  # Call print results at the end of the test

    def measure_consumption(self):
        self.consumption_metrics["network_io_initial"] = self.get_localhostmetrics()
        while self.running:
            self.record_consumption_metrics()
            time.sleep(0.01)
        self.consumption_metrics["network_io_final"] = self.get_localhostmetrics()

    def get_localhostmetrics(self):
        interfaces = psutil.net_io_counters(pernic=True)
        for interface_name in interfaces:
            if interface_name.lower().startswith("lo"):
                return interfaces[interface_name]

    def record_consumption_metrics(self):
        if self.browser_processes:
            self.record_total_consumption(self.browser_processes, "browser")
        if self.node_process:
            self.record_total_consumption(self.node_process, "node")
        if self.tomcat_process:
            self.record_total_consumption(self.tomcat_process, "tomcat")

    def record_total_consumption(self, process, process_name):
        self.record_memory_consumption(process, process_name)
        self.record_cpu_consumption(process, process_name)

    def record_cpu_consumption(self, processes, process_name):
        cpu_usage = 0
        for proc in processes:
            try:
                cpu_usage += proc.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        self.consumption_metrics[f"cpu_usage_{process_name}"].append(cpu_usage)

    def record_memory_consumption(self, processes, process_name):
        memory_usage = 0
        for proc in processes:
            try:
                memory_usage += proc.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        self.consumption_metrics[f"memory_usage_{process_name}"].append(memory_usage)

    def calculate_consumption(self):
        self.consumption_metrics["thread_execution_time"] = time.time() - self.consumption_metrics["thread_start_time"]

    def print_consumption_results(self, testname):
        consumptions = self.get_consumption()

        if self.summary:
            headers = [testname,""]
            alignments = ["left", "right"]
            rows = [
                    ["🌱 Energy Consumption Results", f"{consumptions['total_consumption']:.2f} Ws 🌱"],
                    ["Frontend", ""],
                    ["💻 Browser CPU Consumption", f"{consumptions['browser_cpu_consumption']:.2f} Ws"],
                    ["💭 Browser Memory Consumption", f"{consumptions['browser_memory_consumption']:.2f} Ws"],
                    ["Backend",""], ]


            if self.node_process:
                rows.append(["💻 Node CPU Consumption", f"{consumptions['backend_cpu_consumption']:.2f} Ws"])
                rows.append(["💭 Node Memory Consumption", f"{consumptions['backend_memory_consumption']:.2f} Ws"])
            if self.tomcat_process:
                rows.append(["💻 TomCat CPU Consumption", f"{consumptions['backend_cpu_consumption']:.2f} Ws"])
                rows.append(["💭 TomCat Memory Consumption", f"{consumptions['backend_memory_consumption']:.2f} Ws"])
            self.summary.table(headers, rows, alignments)


            with open(self._output, "w", encoding="utf-8") as f:
                f.write(self.summary.getvalue())

        # Print the results
        print("")
        print(color.CYAN + f"🌱 Energy Consumption Results: {consumptions['total_consumption']:.2f} Ws 🌱" + color.END)
        print("")
        print("Frontend")
        print(f"💻 Browser CPU Consumption: {consumptions['browser_cpu_consumption']:.2f} Ws")
        print(f"💭 Browser Memory Consumption: {consumptions['browser_memory_consumption']:.2f} Ws")
        print("")
        print("Backend")
        if self.node_process:
            print(f"💻 Node CPU Consumption: {consumptions['backend_cpu_consumption']:.2f} Ws")
            print(f"💭 Node Memory Consumption: {consumptions['backend_memory_consumption']:.2f} Ws")

        if self.tomcat_process:
            print(f"💻 TomCat CPU Consumption: {consumptions['backend_cpu_consumption']:.2f} Ws")
            print(f"💭 TomCat Memory Consumption: {consumptions['backend_memory_consumption']:.2f} Ws")

        print("")
        print(f"🌍 Network Consumption: {consumptions['network_consumption']:.2f} Ws")

    def get_consumption(self):
        # Calculate average CPU and Memory consumption
        consumptions = {}

        if self.node_process:
            consumptions["backend_cpu_consumption"] = self.consumption("node", "cpu_usage")
            consumptions["backend_memory_consumption"] = self.consumption("node", "memory_usage")

        if self.tomcat_process:
            consumptions["backend_cpu_consumption"] = self.consumption("tomcat", "cpu_usage")
            consumptions["backend_memory_consumption"] = self.consumption("tomcat", "memory_usage")

        consumptions["browser_cpu_consumption"] = self.consumption("browser", "cpu_usage")
        consumptions["browser_memory_consumption"] = self.consumption("browser", "memory_usage")
        consumptions["network_consumption"] = self.get_network_consumption()
        consumptions["total_consumption"] = (
            consumptions["browser_cpu_consumption"]
            + consumptions["backend_cpu_consumption"]
            + consumptions["browser_memory_consumption"]
            + consumptions["backend_memory_consumption"]
            + consumptions["network_consumption"]
        )

        return consumptions

    def consumption(self, process_name, usage_type):

        if usage_type == "cpu_usage":
            # calculate energy consumptions
            try:
                processor_consumption = self.config["processor"][self.processor]
            except KeyError:
                print(
                    f"\nProcessor '{self.processor}' not found. Using default value of {self.config['processor']['DEFAULT']} Ws."
                )
                processor_consumption = self.DEFAULT_PROCESSOR_CONSUMPTION
            return (
                self.get_average_usage(process_name, usage_type)
                / 100
                * processor_consumption
                * self.consumption_metrics["thread_execution_time"]
            )

        elif usage_type == "memory_usage":
            return (
                self.get_average_usage(process_name, usage_type)
                * self.config["ram"][self.ram]
                * self.consumption_metrics["thread_execution_time"]
            )

    def get_average_usage(self, process_name, usage_type):
        usage = self.consumption_metrics[f"{usage_type}_{process_name}"]
        return sum(usage) / len(usage) if usage else 0

    def get_network_consumption(self):
        print(self.consumption_metrics)
        bytes_sent = (
            self.consumption_metrics["network_io_final"].bytes_sent - self.consumption_metrics["network_io_initial"].bytes_sent
        )
        bytes_received = (
            self.consumption_metrics["network_io_final"].bytes_recv - self.consumption_metrics["network_io_initial"].bytes_recv
        )
        return (bytes_sent + bytes_received) / 1024 / 1024 * self.config["network"]
