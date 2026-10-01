import rtde_control
from robot_control.gripper import robotiq_gripper




class Gripper:
    def activate_gripper(ip_address, port=63352):
        gripper = robotiq_gripper.RobotiqGripper()
        gripper.connect(ip_address, port)
        gripper.activate()
        print("Gripper activated")
        return gripper
    


class DemoStaticPickPlace:

    IP = "192.168.0.20"
    SPEED_FAST = 1
    SPEED_SLOW = 0.5

    # Cube positions and target position
    GREEN_CUBE_POSE = [0.5627132229616074, 0.11596701008253553, 0.24876122165623385, -2.2180565903435605, 2.222198641641369, -0.004145227964218369]
    # OLD: GREEN_CUBE_POSE = [0.7203031126388598, -0.06200542235339407, 0.2262273676576626, -2.2122743344153633, 2.2073320457497303, -0.04578027219250717]
    # ORANGE_CUBE_POSE = [0.546076897569226, 0.10579331434068523, 0.227791821061122, -2.217365794478296, 2.2211521894331345, -0.006537174599903164]
    ORANGE_CUBE_POSE = [0.4760917447925088, 0.11184615426941283, 0.24880910182565846, -2.2143680482786037, 2.2209951626155258, 0.02950518403548811]
    RED_CUBE_POSE = [0.6574531923678613, 0.11551071654555242, 0.24903293561016393, 2.22870297359331, -2.199503316573422, -0.017180771921204426]
    TARGET_POSE = [0.5577107189746524, -0.14468426474747512, 0.24911724698603727, 0.021081459063631788, 3.12212968663113, -0.007024128713232088]



    def __init__(self):
        # Init RTDE control interface
        self.rtde_c = rtde_control.RTDEControlInterface(self.IP)
        self.gripper = Gripper.activate_gripper(ip_address=self.IP)





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
