import cv2 
import socket 
import struct 

def open_camera(): 

    cam = cv2.VideoCapture(0)

    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
    while True: 

        ret, frame = cam.read() 

        cam.set(3, 800)
        cam.set(4, 600)

        out.write(frame)

        cv2.imshow('Camera', frame)

        if cv2.waitKey(1) == ord('q'): 
            break 

    # Release the capture and writer objects
    cam.release()
    out.release()
    cv2.destroyAllWindows()

open_camera() 

