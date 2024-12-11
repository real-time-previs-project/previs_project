import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt 
from usd_view import USDHierarchyView 
#processing.process_video 
import cv2 
import imutils
import processing.poly_dectection 
import numpy as np 
from communication.send_json import start
import communication.web_socket
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

#from poly_detection import process_video_with_polygons
class RatatouilleUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ratatouille with Video and USD Hierarchy")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left Panel (USD Hierarchy and Controls)
        left_panel = QVBoxLayout()

        # Start method from send_json 
        
        self.full_path = ''
        self.hierarchy_view = USDHierarchyView()
        left_panel.addWidget(QLabel("USD Hierarchy"))
        left_panel.addWidget(self.hierarchy_view)
        self.timer = QTimer()  # Initialize the timer here
        self.timer.timeout.connect(self.update_frame)  # Connect the timeout t

        # Video buttons 
        left_panel.addWidget(QLabel("Video Controls"))
        upload_button = QPushButton("Upload Video")
        upload_button.clicked.connect(self.upload_video)
        live_capture_button = QPushButton("Live Capture")
        live_capture_button.clicked.connect(lambda: self.display_video_placeholder(0))
        left_panel.addWidget(upload_button)
        left_panel.addWidget(live_capture_button)
        send_to_hou = QPushButton("Send GEO To Houdini")
        send_to_hou.clicked.connect(self.send_json)
        left_panel.addWidget(send_to_hou)
        

        # Simulation Controls
        sim_label = QLabel("Simulation Setup")
        preset_dropdown = QComboBox()
        preset_dropdown.addItems(["Particles", "Rigid Bodies", "Smoke"])
        gravity_slider = QSlider(Qt.Horizontal)
        gravity_slider.setRange(0, 100)
        gravity_slider.setValue(50)
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setRange(0, 100)
        speed_slider.setValue(50)
        left_panel.addWidget(sim_label)
        left_panel.addWidget(QLabel("Preset"))
        left_panel.addWidget(preset_dropdown)
        left_panel.addWidget(QLabel("Gravity"))
        left_panel.addWidget(gravity_slider)
        left_panel.addWidget(QLabel("Speed"))
        left_panel.addWidget(speed_slider)

        # Timeline Controls
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.seek_frame)
        self.prev_button = QPushButton("<<")
        self.prev_button.clicked.connect(self.step_backward)
        self.next_button = QPushButton(">>")
        self.next_button.clicked.connect(self.step_forward)

        timeline_layout = QHBoxLayout()
        timeline_layout.addWidget(self.prev_button)
        timeline_layout.addWidget(self.timeline_slider)
        timeline_layout.addWidget(self.next_button)
        left_panel.addLayout(timeline_layout)

        # Central Panel (Video Display)
        self.video_display = QLabel("Video/Simulation Preview")
        self.video_display.setStyleSheet("background-color: #000; color: #FFF;")
        self.video_display.setFixedSize(800, 600)

        central_panel = QVBoxLayout()
        central_panel.addWidget(self.video_display)

        # Add Panels to Main Layout
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(central_panel, stretch=3)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def upload_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.mov)")
        if file_path:
            self.display_video_placeholder(file_path)

    def display_video_placeholder(self, video_source):
        """
        Handles video display, either from a file or live capture.

        Parameters:
            video_source: int (e.g., 0 for webcam) or str (file path).
        """
        # Release any previous video capture
        if hasattr(self, "vid") and self.vid.isOpened():
            self.vid.release()

        # Initialize the video capture
        self.vid = cv2.VideoCapture(video_source)
        print(self.vid)

        # Check if the video source is open
        if not self.vid.isOpened():
            print("Error: Unable to open video source.")
            return

            # Get video dimensions
        frame_width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Compute the aspect ratio
        aspect_ratio = frame_width / frame_height

        # Resize QLabel to match aspect ratio
        display_width = 800  # Desired display width
        display_height = int(display_width / aspect_ratio)
        self.video_display.setFixedSize(display_width, display_height)

        # Live Capture: Set total frames to -1 for indefinite streaming
        if isinstance(video_source, int):
            self.total_frames = -1
            self.current_frame = 0
            self.timeline_slider.setDisabled(True)  # Disable timeline for live video
        else:
            self.total_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
            self.current_frame = 0
            self.timeline_slider.setMaximum(self.total_frames - 1)
            self.timeline_slider.setEnabled(True)

        # Start the timer for frame updates
        if not hasattr(self, "timer"):
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Approximately 30 FPS

    def update_frame(self):
        ret, frame = self.vid.read()
        if not ret:
            print("Error: Cannot read frame (end of video or camera issue).")
            self.timer.stop()
            self.vid.release()
            return

        # Resize the frame to fit QLabel
        frame = cv2.resize(frame, (800, 600))

        # Detect polygons in the frame
        polygons = processing.poly_dectection.detect_polygons(frame)

        # Draw polygons on the frame
        for polygon in polygons:
            vertices = polygon["vertices"]

            # Convert vertices to NumPy array
            pts = np.array([[v["x"], v["y"]] for v in vertices], dtype=np.int32)

            # Draw the polygon
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

            # Optionally, draw additional attributes like area (as text)
            area = polygon["attributes"].get("area", 0)
            if area > 0:
                centroid = np.mean(pts, axis=0).astype(int)
                cv2.putText(
                    frame, f"Area: {int(area)}",
                    (centroid[0], centroid[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
                )

        # Convert frame to QImage and display it in QLabel
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_display.setPixmap(QPixmap.fromImage(qimg))


    def send_json(self): 
        print(self.full_path)
        run_houdini_script(self.full_path)

    def json(self, polygons): 
        full_path = processing.poly_dectection.create_houdini_json(polygons, "test.txt")
        return full_path 


    def seek_frame(self, frame_number):
        self.timer.stop()
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number
        self.update_frame()

    def step_forward(self):
        if self.current_frame < self.total_frames - 1:
            self.seek_frame(self.current_frame + 1)

    def step_backward(self):
        if self.current_frame > 0:
            self.seek_frame(self.current_frame - 1)

def run_houdini_script(json_file):
    """
    Runs a Houdini script using hython.
    
    Parameters:
        houdini_script (str): Path to the Houdini Python script to execute.
        input_file (str): Path to the input JSON or data file.
        output_file (str): Path to save the simulation results.
    """
    cmd = [
        "hython", "/Users/masonkirby/Desktop/render_project/src/houdini/api_scripts/import_geo.py",
        json_file
    ]
    try:
        subprocess.run(cmd, check=True)
        #print(f"Houdini script {houdini_script} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Houdini script: {e}")

class FrameProcessingThread(QThread):
    frame_processed = pyqtSignal(np.ndarray, list)  # Signal with frame and polygons

    def __init__(self, vid):
        super().__init__()
        self.vid = vid
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.vid.read()
            if not ret:
                break
            polygons = detect_polygons(frame)
            self.frame_processed.emit(frame, polygons)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = RatatouilleUI()
    ui.show()
    sys.exit(app.exec_())
