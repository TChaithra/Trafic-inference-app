import os
from dotenv import load_dotenv

load_dotenv()

IMX8_HOST = os.getenv('IMX8_HOST', '192.168.1.100')
IMX8_PORT = int(os.getenv('IMX8_PORT', 8001))
IMX8_BASE = f"http://{IMX8_HOST}:{IMX8_PORT}"

BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8000))

MAX_CONCURRENT_JOBS = int(os.getenv('MAX_CONCURRENT_JOBS', 2))
JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', 30))
