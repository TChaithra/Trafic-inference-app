import subprocess
import cv2
import io

def extract_frames(video_path):
    """Extract frames as bytes for batch send (simplified; send one-by-one in prod)"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frames.append(buffer.tobytes())
    cap.release()
    return frames

def reencode_video(frames_bytes, output_path, fps=30, width=640, height=480):
    """Re-encode frames to MP4 using FFmpeg subprocess"""
    subprocess.run([
        'ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-i', '-', 
        '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(fps), 
        '-s', f'{width}x{height}', output_path
    ], input=b''.join(frames_bytes), capture_output=True)
