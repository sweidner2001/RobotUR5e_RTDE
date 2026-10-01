import rtde_control
from robot_control.gripper import robotiq_gripper
import os
import yaml
from pathlib import Path



class Gripper:
    def activate_gripper(ip_address, port=63352):
        gripper = robotiq_gripper.RobotiqGripper()
        gripper.connect(ip_address, port)
        gripper.activate()
        print("Gripper activated")
        return gripper
    


class DemoStaticPickPlace:

    # Speed settings:
    SPEED_FAST = 1
    SPEED_SLOW = 0.5

    # Cube positions:
    GREEN_CUBE_POSE = [0.5627132229616074, 0.11596701008253553, 0.24876122165623385, -2.2180565903435605, 2.222198641641369, -0.004145227964218369]
    ORANGE_CUBE_POSE = [0.4760917447925088, 0.11184615426941283, 0.24880910182565846, -2.2143680482786037, 2.2209951626155258, 0.02950518403548811]
    RED_CUBE_POSE = [0.6574531923678613, 0.11551071654555242, 0.24903293561016393, 2.22870297359331, -2.199503316573422, -0.017180771921204426]
    TARGET_POSE = [0.5577107189746524, -0.14468426474747512, 0.24911724698603727, 0.021081459063631788, 3.12212968663113, -0.007024128713232088]



    def __init__(self):
        self.config = None
        self.config = self.load_config('robot_config.yaml')['robot_params']['rtde_parameters']
        self._init_robot(robot_ip=self.config['robot_ip'])



    def load_config(self, config_file):
        # 1. Config finden (liegt eine Ebene höher als dieses Script)
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(script_dir, '..', 'config', config_file)
        print(f"Config path: {config_path}")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)





    def _init_robot(self, robot_ip=None):
        # Init RTDE control interface
        self.rtde_c = rtde_control.RTDEControlInterface(hostname=robot_ip)
        self.gripper = Gripper.activate_gripper(ip_address=robot_ip)


    def place_cube(self, cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=0, cube_size=0.05, stack_offset=0.001):
        #Move above cube
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+cube_pose_z_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        #Move down to cube
        self.rtde_c.moveL(pose=cube_pose, speed=self.SPEED_SLOW, acceleration=0.3)
        
        # Close gripper 
        self.gripper.move_and_wait_for_pos(position=255, speed=255, force=100)
        
        #Move up with cube
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+cube_pose_z_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        #Move above target
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        #Move down to target
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+stack_position*cube_size+stack_offset, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_SLOW, acceleration=0.3)
        
        # Open gripper
        self.gripper.move_and_wait_for_pos(position=0, speed=100, force=100)
        
        # Move up again
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)



    # back to initial position
    def unplace_cube(self, cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=0, cube_size=0.05, stack_offset=0.001):
        # Move above target
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        # Move down to target
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+stack_position*cube_size+stack_offset, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_SLOW, acceleration=0.3)
        
        # Close gripper 
        self.gripper.move_and_wait_for_pos(position=255, speed=255, force=100)
        
        # Move up with cube
        self.rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        # Move back to initial position
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+cube_pose_z_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        # Move down to empty place
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+stack_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_SLOW, acceleration=0.3)
        
        # Open gripper
        self.gripper.move_and_wait_for_pos(position=0, speed=100, force=100)
        
        # Move up again
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+cube_pose_z_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        


    def stacking_traffic_lights(self):
        self.place_cube(self.GREEN_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=0)
        self.place_cube(self.ORANGE_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=1)
        self.place_cube(self.RED_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=2)


    def unstacking_traffic_lights(self):
        self.unplace_cube(self.RED_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=2)
        self.unplace_cube(self.ORANGE_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=1)
        self.unplace_cube(self.GREEN_CUBE_POSE, self.TARGET_POSE, cube_pose_z_offset=0.1, stack_position=0)


    def move_to_init_pose(self):
        # Move to initial position
        self.rtde_c.moveL(pose=[0.40, 0.0, 0.40, 0.0, 3.12, 0.0], speed=0.1, acceleration=0.3)


if __name__ == "__main__":

    demo = DemoStaticPickPlace()

    for idx in range(3):
        demo.move_to_init_pose()
        demo.stacking_traffic_lights()
        demo.unstacking_traffic_lights()    
