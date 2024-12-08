import cv2
import imutils

def detect_polygons(frame):
    """Detect polygons in a single video frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    polygons = []
    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if cv2.contourArea(approx) > 100:  # Filter small polygons
            vertices = [{"x": int(pt[0][0]), "y": int(pt[0][1])} for pt in approx]
            polygons.append({
                "vertices": vertices,
                "attributes": {
                    "area": cv2.contourArea(approx),
                    "color": [0, 255, 0]  # Example: Placeholder for color
                }
            })
            print(polygons)
    return polygons

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
    