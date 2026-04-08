from pathlib import Path
import sys

import rtde_control
import rtde_receive

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robot_control.gripper import robotiq_gripper

rtde_c = rtde_control.RTDEControlInterface("192.168.0.20")
# 6d pose (x, y, z, Rx, Ry, Rz)
rtde_c.moveL(pose=[0.40, 0.0, 0.40, 0.0, 3.12, 0.0], speed=0.05, acceleration=0.3)
