import cv2
from fastapi import Response
from fastapi.responses import StreamingResponse
import threading
import time

class MJPEGStream:
    def __init__(self, source_url, inference_engine):
        self.source_url = source_url
        self.inference = inference_engine
        self.cap = cv2.VideoCapture(source_url)
        self.running = False
        self.frame = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        def capture_loop():
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        detections = self.inference.infer(frame)
                        self.frame = self.inference.draw_boxes(frame.copy(), detections)
                time.sleep(0.033)  # ~30 FPS
        threading.Thread(target=capture_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.cap.release()

    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frame)
                if ret:
                    return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
        return b''

    def stream_gen(self):
        while True:
            frame_bytes = self.get_frame()
            if frame_bytes:
                yield frame_bytes
            time.sleep(0.033)
