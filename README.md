# RobotUR5e_RTDE
Control Universal Robots UR5e robot with RTDE (Universal Robots API) from external PC


## Setup
to create the Python Environment, start the following scirpt.
```bash
bash setup.sh
```
- The Script creates a `sys-code.pth` file in [.venv/lib/]() with your project root, e.g. `/home/robotur5e/Schreibtisch/RobotUR5e_RTDE/sys-code`.
- Due this, you can import your own python modules with the absolute path from the project root, e.g. `from robot_control.gripper import robotiq_gripper`
- Your file can placed and executed in any sub direcutory and the import still works, both with the shell or the 'Run button' in VSCode.
