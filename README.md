# Energy Meter for Robot Framework

## Overview
The `energyMeter.py` is a custom listener for the Robot Framework, for Energy Consumption Testing (EC Testing). It is designed to monitor and calculate the energy consumption of specific processes during test execution. It focuses on tracking CPU and memory usage, as well as network I/O, for browser and Node.js processes.

## Prerequisites
- Python 3.x
- Robot Framework
- `psutil` Python package
- Node.js
- For Windows users: `wmi` Python package

## Starting the Node.js Service
Before running tests with the Robot Framework, ensure that the Node.js service is up and running. You can initialize and start the service by running the following command in your project directory:

```bash
cd SUTs/Prime-numbers-JS
node init
node index.js
```
This will start the Node.js service. To confirm that the service is running, you can open a web browser and navigate to http://localhost:3000/. If the service is up, you should be able to see the webpage served by your Node.js application.

Ensure that this service is running for the energyMeter listener to monitor its performance during tests.

## Installation
1. Ensure you have Python and Robot Framework installed on your system.
2. Install the required Python packages:
```bash
pip install psutil
# For Windows users:
pip install wmi
```

## Usage
The listener can be used by adding it to your Robot Framework test command using the `--listener` option. Here is an example command:
```bash
robot --listener energyMeter.py prime_number.robot
```
In this scenario, `prime_number.robot` is your test suite file. When executed, `energyMeter.py` will monitor the energy consumption of browser and Node.js processes during the test runs.

## Specific Use-Case
The energyMeter listener is designed to monitor and calculate the energy consumption of specific processes during test execution. In its latest version, it is optimized for scenarios involving prime number calculations.

### Overview
The test scenario involves a web page with the following components:
- A field where you can specify the number of prime numbers you need.
- Two buttons: one to request all prime numbers up to the specified count, and another to request the next prime number in sequence.

### Functionality
- **Requesting All Prime Numbers**: When you input the desired count of prime numbers and click the corresponding button, the frontend sends a request to the backend. The backend responds with a list of all prime numbers up to the specified count.

- **Requesting Next Prime Number**: Clicking the other button sends a request to the backend for the next prime number in sequence. The backend returns the next prime number, and this process continues until all requested prime numbers are received. This feature generates traffic to simulate real-world usage.

### End User Experience
From an end user perspective, the functionality remains the same. Users can still request prime numbers, but now they have the option to request all prime numbers or receive them one by one. This flexibility allows for comprehensive testing of the application's prime number calculation capabilities.

### Usage Example
Here's an example of how to use the energyMeter listener in your Robot Framework test command with the updated use-case:

```bash
robot --listener energyMeter.py prime_number.robot
```
During the test execution, the energyMeter listener will monitor the energy consumption of the processes involved in the prime number calculation scenario, providing valuable insights into resource usage and efficiency.

## Features
* Monitors CPU and memory usage of browser and Node.js processes.
* Calculates network I/O statistics.
* Outputs energy consumption data at the end of the test.

## Output
At the end of the test execution, the script prints out a detailed report of the energy consumption, including CPU, memory, and network usage for both the frontend (browser) and backend (Node.js) processes.
![1702541968572](https://github.com/TheProjectAurora/energy-meter/assets/1047173/6368e898-e928-40bb-9466-55789b3a232a)

## Contributing
Contributions to enhance energyCalculator.py are welcome. Please submit your pull requests or issues to the repository.
