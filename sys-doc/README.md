# RobotUR5e_RTDE
Control Universal Robots UR5e robot with RTDE (Universal Robots API) from external PC


### Project Setup

1. Install dependencies to compile and build C++ packages for the `ur-rtde` package: 
    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential cmake libboost-all-dev python3-dev python3-venv
    ``` 


2. Set up the `.venv` using the script [setup.sh](../setup.sh). The script creates the `.venv` and installs all dependencies listed in [requirements.txt](../requirements.txt). It also adds the code root directory to the `.venv` so that both absolute and relative imports are available from any folder, allowing you to run scripts directly via the 'Run' button in VS Code.

   ```bash
   bash setup.sh
   ```

    - The Script creates a `sys-code.pth` file in [.venv/lib/]() with your project root, e.g. `/home/robotur5e/Schreibtisch/RobotUR5e_RTDE/sys-code`.
    - Due this, you can import your own python modules with the absolute path from the project root, e.g. `from robot_control.gripper import robotiq_gripper`
    - Your file can placed and executed in any sub direcutory and the import still works, both with the shell or the 'Run button' in VSCode.

   <details open>
   <summary><b>Error Handling</b></summary>
      If you get an error stating that you need to install a package to create a `.venv`, run:

      ```bash
      sudo apt update
      sudo apt install python3-venv
      ```

      In some cases, you must make the script executable by running the command:
      ```bash
      chmod +x setup.sh
      ``` 
   </details>

2. Activate the `.venv`:

   ```bash
   source .venv/bin/activate
   ```





---

### Useful Commands

#### requirements.txt

Update [requirements.txt](../requirements.txt):

```bash
pip freeze > requirements.txt

# or:
pip list --format=freeze > requirements.txt
```

#### PyCache

Clear all `__pycache__` files in your project:

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
```