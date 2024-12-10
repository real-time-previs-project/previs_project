import cv2
import imutils
import json 
import asyncio 

def detect_polygons(frame):
    """Detect polygons in a single video frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_of_geos = 0 
    polygons = []
    for contour in contours:

        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if cv2.contourArea(approx) > 100:  # Filter small polygons
            vertices = [{"x": int(pt[0][0]), "y": int(pt[0][1])} for pt in approx]
            num_of_geos += 1 
            polygons.append({
                "Name" : num_of_geos,
                "vertices": vertices,
                "attributes": {
                    "area": cv2.contourArea(approx),
                    "color": [0, 255, 0]  # Example: Placeholder for color
                }
            })
    return polygons

def create_houdini_json(data, output_file):
    """Save extracted video data as JSON for Houdini."""
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)
    print(f"JSON saved to {output_file}")


def process_video(video_path):
    """Process a video and extract geometry data for each frame."""
    vid = cv2.VideoCapture(video_path)
    frame_number = 0
    all_geometry = []

    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break

        frame = imutils.resize(frame, height=400)
        polygons = detect_polygons(frame)

        all_geometry.append({
            "frame": frame_number,
            "geometry": polygons
        })

        frame_number += 1

    vid.release()
    return all_geometry
    