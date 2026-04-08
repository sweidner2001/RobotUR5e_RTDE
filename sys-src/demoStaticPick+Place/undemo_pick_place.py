import rtde_control
import robotiq_gripper

IP = "192.168.0.20"

SPEED_FAST = 1
SPEED_SLOW = 0.5

# Init gripper
# Init gripper
def activate_gripper(ip_address, port=63352):
    gripper = robotiq_gripper.RobotiqGripper()
    gripper.connect(ip_address, port)
    gripper.activate()
    print("Gripper activated")
    return gripper


# Init RTDE control interface
rtde_c = rtde_control.RTDEControlInterface(IP)
gripper = activate_gripper(ip_address=IP)

# Define cube and target poses
green_cube_pose = [0.7203031126388598, -0.06200542235339407, 0.2262273676576626, -2.2122743344153633, 2.2073320457497303, -0.04578027219250717]
orange_cube_pose = [0.546076897569226, 0.10579331434068523, 0.227791821061122, -2.217365794478296, 2.2211521894331345, -0.006537174599903164]
red_cube_pose = [0.6816956855841501, 0.06513999277424651, 0.22789807272749696, 2.2338886805400917, -2.2075560324140544, 0.009118375571405407]
target_pose = [0.5444430205686733, -0.13796004809361231, 0.22622544638457637, -2.2342964896798456, 2.2039816889274517, -0.020637988724632735]


# back to initial position
def unplace_cube(cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=0, cube_size=0.05, stack_offset=0.001):
    # Move above target
    rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=SPEED_FAST, acceleration=0.3)
    # Move down to target
    rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+stack_position*cube_size+stack_offset, target_pose[3], target_pose[4], target_pose[5]], speed=SPEED_SLOW, acceleration=0.3)
    # Close gripper 
    gripper.move_and_wait_for_pos(position=255, speed=255, force=100)
    # Move up with cube
    rtde_c.moveL(pose=[target_pose[0], target_pose[1], target_pose[2]+cube_pose_z_offset+stack_position*cube_size, target_pose[3], target_pose[4], target_pose[5]], speed=SPEED_FAST, acceleration=0.3)
    # Move back to initial position
    rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2], cube_pose[3], cube_pose[4], cube_pose[5]], speed=SPEED_FAST, acceleration=0.3)
    # Move down to cube
    rtde_c.moveL(pose=cube_pose, speed=SPEED_SLOW, acceleration=0.3)
    # Open gripper
    gripper.move_and_wait_for_pos(position=0, speed=100, force=100)
    # Move up again
    rtde_c.moveL(pose=[cube_pose[0], cube_pose[1], cube_pose[2]+cube_pose_z_offset, cube_pose[3], cube_pose[4], cube_pose[5]], speed=SPEED_FAST, acceleration=0.3)
    
unplace_cube(red_cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=2)
unplace_cube(orange_cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=1)
unplace_cube(green_cube_pose, target_pose, cube_pose_z_offset=0.1, stack_position=0)