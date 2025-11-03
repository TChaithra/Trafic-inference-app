from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import uuid
import os
from workers import background_worker, jobs
from config import BACKEND_HOST, BACKEND_PORT, IMX8_BASE
import threading
import httpx

app = FastAPI(title="Backend API")

@app.post("/api/process/upload")
async def process_upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'processing', 'result_url': None}
    
    def worker():
        with open(f'temp_{job_id}.mp4', 'wb') as f:
            f.write(await file.read())
        background_worker(job_id, 'upload', f'temp_{job_id}.mp4')
    
    threading.Thread(target=worker, daemon=True).start()
    return {"job_id": job_id}

@app.post("/api/process/live")
async def process_live(request: dict):
    source_url = request.get("source_url")
    if not source_url:
        raise HTTPException(400, "Missing source_url")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'processing', 'result_url': None}
    
    threading.Thread(target=lambda: background_worker(job_id, 'live', {"source_url": source_url}), daemon=True).start()
    return {"job_id": job_id}

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]

@app.get("/api/result_file/{job_id}")
async def get_result_file(job_id: str):
    if job_id not in jobs or 'completed' != jobs[job_id]['status']:
        raise HTTPException(404, "Not ready")
    return FileResponse(f'temp_{job_id}.mp4', media_type="video/mp4")

@app.get("/api/stream/{job_id}")
async def proxy_stream(job_id: str):
    if job_id not in jobs or not jobs[job_id]['result_url'].startswith(IMX8_BASE):
        raise HTTPException(404, "No stream")
    stream_url = jobs[job_id]['result_url']
    async with httpx.AsyncClient() as client:
        req = client.build_request("GET", stream_url)
        resp = await client.send(req, stream=True)
        return StreamingResponse(resp.aiter_bytes(), headers=dict(resp.headers))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
