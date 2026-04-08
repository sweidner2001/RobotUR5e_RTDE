import rtde_control
import rtde_receive
import robotiq_gripper

rtde_c = rtde_control.RTDEControlInterface("192.168.0.20")
# 6d pose (x, y, z, Rx, Ry, Rz)
rtde_c.moveL(pose=[0.40, 0.0, 0.40, 0.0, 3.12, 0.0], speed=0.05, acceleration=0.3)
