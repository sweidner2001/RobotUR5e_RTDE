# RobotUR5e_RTDE
Control Universal Robots UR5e robot with RTDE (Universal Robots API) from external PC


## Setup
1. Install dependencies to compile and build C++ packages for the `ur-rtde` package: 
    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential cmake libboost-all-dev python3-dev python3-venv
    ``` 


2. Create the Python Environment. Start the following scirpt:
    ```bash
    bash setup.sh
    ```
- The Script creates a `sys-code.pth` file in [.venv/lib/]() with your project root, e.g. `/home/robotur5e/Schreibtisch/RobotUR5e_RTDE/sys-code`.
- Due this, you can import your own python modules with the absolute path from the project root, e.g. `from robot_control.gripper import robotiq_gripper`
- Your file can placed and executed in any sub direcutory and the import still works, both with the shell or the 'Run button' in VSCode.
