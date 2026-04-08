import rtde_receive

IP = "192.168.0.20"

rtde_r = rtde_receive.RTDEReceiveInterface(IP)
print(f"Current TCP pose: {rtde_r.getActualTCPPose()}")