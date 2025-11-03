import httpx
import asyncio
from config import IMX8_BASE, JOB_TIMEOUT, MAX_CONCURRENT_JOBS
from utils import extract_frames, reencode_video
import threading
from concurrent.futures import ThreadPoolExecutor

# Semaphore for concurrency
sem = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

jobs = {}  # job_id -> {'status': str, 'result_url': str or None}

async def forward_to_imx8(job_id, task_type, data):
    async with sem:
        try:
            async with httpx.AsyncClient(timeout=JOB_TIMEOUT) as client:
                if task_type == 'frame':  # Not used directly
                    pass
                elif task_type == 'upload':
                    resp = await client.post(f"{IMX8_BASE}/process_file", files={'file': ('video.mp4', data)})
                    if resp.status_code == 200:
                        with open(f'temp_{job_id}.mp4', 'wb') as f:
                            f.write(resp.content)
                        jobs[job_id]['result_url'] = f'/api/result_file/{job_id}'
                elif task_type == 'live':
                    resp = await client.post(f"{IMX8_BASE}/process_stream", json=data)
                    if resp.status_code == 200:
                        stream_url = resp.json()['stream_url']
                        jobs[job_id]['result_url'] = stream_url
                jobs[job_id]['status'] = 'completed'
        except Exception as e:
            jobs[job_id]['status'] = f'failed: {str(e)}'

def background_worker(job_id, task_type, data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(forward_to_imx8(job_id, task_type, data))
    loop.close()
