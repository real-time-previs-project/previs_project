import cv2
import os

def overlay_simulation(video_path, sim_frames_dir, output_path):
    # Open the original video
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Unable to open video.")
        return

    # Get video properties
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))

    # Set up video writer for the output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Load simulation frames
    sim_frames = sorted([os.path.join(sim_frames_dir, f) for f in os.listdir(sim_frames_dir) if f.endswith(".png")])

    # Process each frame
    frame_index = 0
    while True:
        ret, video_frame = video.read()
        if not ret:
            break

        # Resize the simulation frame to match the video frame
        if frame_index < len(sim_frames):
            sim_frame = cv2.imread(sim_frames[frame_index], cv2.IMREAD_UNCHANGED)

            # Separate alpha channel for transparency
            if sim_frame.shape[2] == 4:  # Ensure the image has an alpha channel
                alpha = sim_frame[:, :, 3] / 255.0
                sim_frame = sim_frame[:, :, :3]  # Drop the alpha channel

                # Composite the simulation frame over the video frame
                for c in range(0, 3):
                    video_frame[:, :, c] = (alpha * sim_frame[:, :, c] + 
                                            (1 - alpha) * video_frame[:, :, c])

        # Write the composite frame to the output video
        out.write(video_frame)

        frame_index += 1

    # Release resources
    video.release()
    out.release()
    print(f"Overlay video saved to {output_path}")
