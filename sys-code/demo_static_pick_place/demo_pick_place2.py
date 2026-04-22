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
    GREEN_CUBE_POSE = [0.7266856000383094, -0.06528322174343981, 0.2283489278836398, -2.2317014531059445, 2.2046761897580267, -0.008747817800563374]
    # OLD: GREEN_CUBE_POSE = [0.7203031126388598, -0.06200542235339407, 0.2262273676576626, -2.2122743344153633, 2.2073320457497303, -0.04578027219250717]
    ORANGE_CUBE_POSE = [0.546076897569226, 0.10579331434068523, 0.227791821061122, -2.217365794478296, 2.2211521894331345, -0.006537174599903164]
    RED_CUBE_POSE = [0.6816956855841501, 0.06513999277424651, 0.22789807272749696, 2.2338886805400917, -2.2075560324140544, 0.009118375571405407]
    TARGET_POSE = [0.5444430205686733, -0.13796004809361231, 0.22622544638457637, -2.2342964896798456, 2.2039816889274517, -0.020637988724632735]



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
        self.rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2], cube_pose[3], cube_pose[4], cube_pose[5]], speed=self.SPEED_FAST, acceleration=0.3)
        # Move down to cube
        self.rtde_c.moveL(pose=cube_pose, speed=self.SPEED_SLOW, acceleration=0.3)
        
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
