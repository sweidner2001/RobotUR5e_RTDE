import time
import imagingcontrol4 as ic4

def main():
    # Initialize the IC Imaging Control 4 library
    ic4.Library.init()

    try:
        # Create a Grabber object to control the camera
        grabber = ic4.Grabber()

        # Check for connected devices
        devices = ic4.DeviceEnum.devices()
        if not devices:
            print("No cameras found. Please check your USB 3.0 connection.")
            return

        # Open the first available device (e.g., DFK 33UX273)
        print(f"Opening device: {devices[0].model_name} (Serial: {devices[0].serial})")
        grabber.device_open(devices[0])

        # Create a SnapSink to receive frames from the stream
        sink = ic4.SnapSink()

        # Setup the data stream and start acquisition immediately
        grabber.stream_setup(sink, setup_option=ic4.StreamSetupOption.ACQUISITION_START)
        print("Stream started successfully. Grabbing frames...")

        # Stream loop: Grab 50 frames sequentially
        for i in range(50):
            try:
                # Wait up to 1000 ms for the next image frame
                image = sink.snap_single(1000)
                
                # Print basic frame metadata
                print(f"Frame {i+1} captured: Width={image.width}, Height={image.height}, Format={image.pixel_format}")
                
                # Optional: If you want to convert it to a NumPy array for OpenCV/processing:
                # arr = image.numpy_wrap()
                
            except ic4.IC4Exception as ex:
                print(f"Timeout or error grabbing frame {i+1}: {ex.message}")

        # Stop the stream and close the device
        grabber.stream_stop()
        grabber.device_close()
        print("Stream stopped and device closed cleanly.")

    except ic4.IC4Exception as ex:
        print(f"An error occurred: {ex.message}")
    
    finally:
        # Exit library context
        ic4.Library.exit()

if __name__ == "__main__":
    main()