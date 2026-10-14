from robot_control.gripper import robotiq_gripper
from config.Config import Config




    
def log_info(gripper):
    print(f"Pos: {str(gripper.get_current_position()): >3}  "
          f"Open: {gripper.is_open(): <2}  "
          f"Closed: {gripper.is_closed(): <2}  ")


print("Creating gripper...")
config = Config('robot_config.yaml').get_config()['robot_params']['rtde_parameters']
gripper = robotiq_gripper.RobotiqGripper()

print("Connecting to gripper...")
gripper.connect(config['robot_ip'], config['gripper_port'])

print("Activating gripper...")
gripper.activate()

print("Testing gripper...")
gripper.move_and_wait_for_pos(255, 255, 255)
log_info(gripper)
gripper.move_and_wait_for_pos(0, 255, 255)
log_info(gripper)