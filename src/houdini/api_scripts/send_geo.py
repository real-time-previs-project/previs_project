import cv2
import imutils
import requests

def send_geometry_to_houdini(video_path, endpoint="http://localhost:5000/send_geometry"):
    geometry_data = process_video(video_path)

    for frame_data in geometry_data:
        response = requests.post(endpoint, json=frame_data)
        if response.status_code == 200:
            print(f"Frame {frame_data['frame']} processed successfully.")
        else:
            print(f"Error processing frame {frame_data['frame']}: {response.text}")

if __name__ == "__main__":
    video_path = "path_to_your_video.mp4"
    send_geometry_to_houdini(video_path)
