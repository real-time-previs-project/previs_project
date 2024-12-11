import cv2
import numpy as np
import pyrealsense2 as rs

def depth_map(): 
    # Load stereo images (left and right)
    left_image = cv2.imread('left.jpg', cv2.IMREAD_GRAYSCALE)
    right_image = cv2.imread('right.jpg', cv2.IMREAD_GRAYSCALE)

    # Initialize the stereo block matcher
    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

    # Compute disparity map
    disparity = stereo.compute(left_image, right_image)

    # Normalize the disparity map for visualization
    disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Display results
    cv2.imshow('Disparity Map', disparity_normalized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def lidar_map(): 
    # Initialize RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()

    # Configure LiDAR (depth) stream
    config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)

    try:
        while True:
            # Wait for frames
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                continue

            # Convert depth frame to numpy array
            depth_image = np.asanyarray(depth_frame.get_data())

            # Apply colormap for visualization
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # Display the depth colormap
            cv2.imshow("LiDAR Depth Stream", depth_colormap)

            # Exit on key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()
