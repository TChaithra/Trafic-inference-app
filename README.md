# Trafic-inference-app
Creating end to end web application



Traffic Video Inference Web App
This project provides an end-to-end web application for processing traffic videos or live RTSP streams using a YOLO-based TFLite model on an NXP i.MX8M+ board's NPU.
Prerequisites

i.MX8M+ board with Yocto Linux (e.g., from NXP eIQ Toolkit v2.0+).
Python 3.9+ on IMX8 and host.
Node.js 18+ for frontend.
FFmpeg installed on IMX8 and host (via apt install ffmpeg or Yocto recipe).
Your converted TFLite model (model.tflite) ready.
Network: IMX8 and host on same LAN.

Step-by-Step Setup and Deployment
1. Clone and Prepare the Repository
text
git clone <this-repo> traffic-inference-app
cd traffic-inference-app
cp .env.example .env

Edit .env: Set IMX8_HOST to your board's IP. Copy to IMX8 as well.
Place your model.tflite in imx8_service/model/.

2. IMX8M+ Setup (On the Board)
2.1 Install Dependencies
Connect to IMX8 via SSH. Install eIQ Toolkit if not already (follow NXP docs: download from nxp.com/eiq, build Yocto image with meta-ml layer).
For NPU delegate:

Ensure Vivante NPU drivers are loaded: lsmod | grep galcore.
The delegate lib (libvx_delegate.so) is in /usr/lib/ after eIQ build.

Install Python deps:
text
pip install -r imx8_service/requirements.txt
Note: Use tflite-runtime (not full TF) for efficiency. If issues, build from eIQ sources.

2.2 Configure and Test Inference

Edit env on IMX8: export MODEL_PATH=./model/model.tflite and DELEGATE_PATH=/usr/lib/libvx_delegate.so.
Test standalone inference:

python -c "
from inference import YOLOInference
inf = YOLOInference(os.getenv('MODEL_PATH'), os.getenv('DELEGATE_PATH'))
import cv2
img = cv2.imread('test.jpg')
dets = inf.infer(img)
print(dets)
"

Verify NPU usage: Run with tegrastats or check logs for delegate loading.

2.3 Deploy IMX8 Service

cd imx8_service
uvicorn main:app --host 0.0.0.0 --port 8001
Test endpoints:

Frame: curl -X POST -F "file=@test.jpg" http://<imx8-ip>:8001/infer/frame --output processed.jpg
Video: Similar for /process_file.
Stream: curl -X POST -H "Content-Type: application/json" -d '{"source_url":"rtsp://test"}' http://<imx8-ip>:8001/process_stream



3. Backend Setup (On Host/Server)

4. 3.2 Deploy Backend
text
npm run dev

Access at http://localhost:3000.
Test modes: Upload a video file; enter RTSP URL (e.g., rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4 for sample).

5. Full End-to-End Testing
5.1 Sample Video Test

Download sample: wget https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4 -O sample.mp4
Run IMX8 service.
Run backend.
Run frontend, switch to Upload, select sample.mp4, process. View overlaid video.

5.2 Sample RTSP Stream Test

Use public RTSP: rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov
Run services as above.
Frontend Live mode: Enter URL, start. View MJPEG stream with boxes.

5.3 Troubleshooting

Timeouts: Increase JOB_TIMEOUT if videos are long.
Concurrency: MAX_CONCURRENT_JOBS=1 for testing.
Logs: Check uvicorn output for errors.
NPU: If delegate fails, fallback to CPU by removing experimental_delegates.
FFmpeg: Ensure on path; errors if missing.
Cleanup: Jobs store temp files; add cron to rm temp_*.mp4.

6. Production Notes

Scale: Use Celery + Redis for workers.
Security: Add API keys, HTTPS.
Monitoring: Add Prometheus.
HLS Alternative: Replace MJPEG with FFmpeg HLS in stream_handler.py for better browser support.

This completes the setup from start (prereqs) to end (testing). For customizations, plug your YOLO postprocess into inference.py. Contact if issues!
3.1 Install Dependencies

   cd backend
pip install -r requirements.txt
