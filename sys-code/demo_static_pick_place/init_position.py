import rtde_control
from robot_control.gripper import robotiq_gripper
from config.Config import Config


config = Config('robot_config.yaml').get_config()['robot_params']['rtde_parameters']

       
rtde_c = rtde_control.RTDEControlInterface(config['robot_ip'])
# 6d pose (x, y, z, Rx, Ry, Rz)
rtde_c.moveL(pose=[0.40, 0.0, 0.50, 0.0, 3.12, 0.0], speed=0.1, acceleration=0.3)
