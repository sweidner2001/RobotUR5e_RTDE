import rtde_receive
from config.Config import Config


config = Config('robot_config.yaml').get_config()['robot_params']['rtde_parameters']


rtde_r = rtde_receive.RTDEReceiveInterface(config['robot_ip'])
print(f"Current TCP pose: {rtde_r.getActualTCPPose()}")