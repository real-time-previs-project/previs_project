import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt 
from usd_view import USDHierarchyView  # Import the new hierarchy class
import cv2 
import imutils
from poly_dectection import detect_polygons
import numpy as np 
from processing.send_json import start


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

        self.hierarchy_view = USDHierarchyView()
        left_panel.addWidget(QLabel("USD Hierarchy"))
        left_panel.addWidget(self.hierarchy_view)
        self.timer = QTimer()  # Initialize the timer here
        self.timer.timeout.connect(self.update_frame)  # Connect the timeout t

        left_panel.addWidget(QLabel("Video Controls"))
        upload_button = QPushButton("Upload Video")
        upload_button.clicked.connect(self.upload_video)
        live_capture_button = QPushButton("Live Capture")
        live_capture_button.clicked.connect(lambda: self.display_video_placeholder(0))
        left_panel.addWidget(upload_button)
        left_panel.addWidget(live_capture_button)

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

    def display_video_placeholder(self, video_path):
        self.vid = cv2.VideoCapture(video_path)

        if not self.vid.isOpened():
            print("Error: Unable to open video source.")
            return

        self.total_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.timeline_slider.setMaximum(self.total_frames - 1)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.vid.read()
        if not ret:
            print("End of video or cannot read frame.")
            self.timer.stop()
            self.vid.release()
            return

        # Resize the frame to fit QLabel
        frame = cv2.resize(frame, (800, 600))

        # Detect polygons in the frame
        polygons = detect_polygons(frame)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = RatatouilleUI()
    ui.show()
    sys.exit(app.exec_())
