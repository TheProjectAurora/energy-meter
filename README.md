# Energy Calculator for Robot Framework

## Overview
The `energyCalculator.py` is a custom listener for the Robot Framework, designed to monitor and calculate the energy consumption of specific processes during test execution. It focuses on tracking CPU and memory usage, as well as network I/O, for browser and Node.js processes.

## Prerequisites
- Python 3.x
- Robot Framework
- `psutil` Python package
- Node.js
- For Windows users: `wmi` Python package

## Starting the Node.js Service
Before running tests with the Robot Framework, ensure that the Node.js service is up and running. You can start the service by running the following command in your project directory:

```bash
cd SUT
node index.js
```
This will start the Node.js service. To confirm that the service is running, you can open a web browser and navigate to http://localhost:3000/. If the service is up, you should be able to see the webpage served by your Node.js application.

Ensure that this service is running for the energyCalculator listener to monitor its performance during tests.

## Installation
1. Ensure you have Python and Robot Framework installed on your system.
2. Install the required Python packages:
```bash
pip install psutil
# For Windows users:
pip install wmi
```
3. Download `energyCalculator.py` and place it in your project directory.

## Usage
The listener can be used by adding it to your Robot Framework test command using the `--listener` option. Here is an example command:
```bash
robot --listener energyCalculator.py merry_christmas.robot
```
In this scenario, `merry_christmas.robot` is your test suite file. When executed, `energyCalculator.py` will monitor the energy consumption of browser and Node.js processes during the test runs.

## Specific Use-Case
For a web page containing two images - one static and one a moving GIF - the listener will track the energy consumed by these processes to render and manage these images.

## Features
* Monitors CPU and memory usage of browser and Node.js processes.
* Calculates network I/O statistics.
* Outputs energy consumption data at the end of the test.

## Output
At the end of the test execution, the script prints out a detailed report of the energy consumption, including CPU, memory, and network usage for both the frontend (browser) and backend (Node.js) processes.
![image](https://github.com/NorthCodeLtd/energy_calculator/assets/1047173/dec7d4ea-5b5e-4613-85cc-9139413ad707)

## Contributing
Contributions to enhance energyCalculator.py are welcome. Please submit your pull requests or issues to the repository.
