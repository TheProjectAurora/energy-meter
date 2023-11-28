# Energy Calculator for Robot Framework

## Overview
The `energyCalculator.py` is a custom listener for the Robot Framework, designed to monitor and calculate the energy consumption of specific processes during test execution. It focuses on tracking CPU and memory usage, as well as network I/O, for browser and Node.js processes.

## Prerequisites
- Python 3.x
- Robot Framework
- `psutil` Python package
- For Windows users: `wmi` Python package

## Installation
1. Ensure you have Python and Robot Framework installed on your system.
2. Install the required Python packages:
   # Energy Calculator for Robot Framework

## Overview
The `energyCalculator.py` is a custom listener for the Robot Framework, designed to monitor and calculate the energy consumption of specific processes during test execution. It focuses on tracking CPU and memory usage, as well as network I/O, for browser and Node.js processes.

## Prerequisites
- Python 3.x
- Robot Framework
- `psutil` Python package
- For Windows users: `wmi` Python package

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
![Screenshot 2023-11-28 144440](https://github.com/NorthCodeLtd/energy_calculator/assets/1047173/0c210ebb-3548-40b6-b1d2-a00553b9e895)


## Contributing
Contributions to enhance energyCalculator.py are welcome. Please submit your pull requests or issues to the repository.
