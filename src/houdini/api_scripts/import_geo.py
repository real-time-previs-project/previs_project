import cv2
import imutils
import requests

from flask import Flask, request, jsonify
import hou

app = Flask(__name__)

@app.route('/send_geometry', methods=['POST'])
def send_geometry():
    data = request.json
    frame = data["frame"]
    geometry = data["geometry"]



    return jsonify({"status": "success", "message": f"Geometry for frame {frame} processed."})

if __name__ == "__main__":
    app.run(port=5000)


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
