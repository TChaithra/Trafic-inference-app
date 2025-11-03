from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import io
import os
from inference import YOLOInference
from stream_handler import MJPEGStream
from PIL import Image
import numpy as np
from datetime import datetime

app = FastAPI(title="IMX8 Inference Service")

# Load config
MODEL_PATH = os.getenv('MODEL_PATH', './model/model.tflite')
DELEGATE_PATH = os.getenv('DELEGATE_PATH', '/usr/lib/libvx_delegate.so')
inference_engine = YOLOInference(MODEL_PATH, DELEGATE_PATH)

streams = {}  # stream_id -> MJPEGStream

@app.post("/infer/frame")
async def infer_frame(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Invalid image")
    detections = inference_engine.infer(image)
    processed = inference_engine.draw_boxes(image, detections)
    _, buffer = cv2.imencode('.jpg', processed)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")

@app.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    contents = await file.read()
    cap = cv2.VideoCapture()
    cap.open(io.BytesIO(contents), cv2.CAP_FFMPEG)  # FFMPEG backend
    if not cap.isOpened():
        raise HTTPException(400, "Invalid video")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter('processed.mp4', fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        detections = inference_engine.infer(frame)
        processed = inference_engine.draw_boxes(frame, detections)
        out.write(processed)
    
    cap.release()
    out.release()
    
    with open('processed.mp4', 'rb') as f:
        return StreamingResponse(f, media_type="video/mp4")

@app.post("/process_stream")
async def process_stream(request: dict):
    source_url = request.get("source_url")
    if not source_url:
        raise HTTPException(400, "Missing source_url")
    
    stream_id = f"{datetime.now().timestamp()}"
    stream = MJPEGStream(source_url, inference_engine)
    stream.start()
    streams[stream_id] = stream
    
    # Cleanup after timeout (simple; use scheduler in prod)
    threading.Timer(300, lambda: streams.pop(stream_id, None) and stream.stop()).start()  # 5min
    
    stream_url = f"http://{os.getenv('IMX8_HOST', 'localhost')}:{os.getenv('IMX8_PORT', 8001)}/stream/{stream_id}"
    return {"stream_url": stream_url}

@app.get("/stream/{stream_id}")
async def stream_mjpeg(stream_id: str):
    if stream_id not in streams:
        raise HTTPException(404, "Stream not found")
    stream = streams[stream_id]
    
    def event_stream():
        yield b'HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n'
        for frame in stream.stream_gen():
            yield frame
        yield b'\r\n'
    
    return StreamingResponse(event_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
