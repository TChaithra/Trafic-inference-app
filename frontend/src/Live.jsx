import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Live() {
  const [url, setUrl] = useState('')
  const [jobId, setJobId] = useState(null)
  const [streamUrl, setStreamUrl] = useState('')

  const handleSubmit = async () => {
    const resp = await fetch(`${API_URL}/api/process/live`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_url: url })
    })
    const data = await resp.json()
    setJobId(data.job_id)
    pollStream(data.job_id)
  }

  const pollStream = async (id) => {
    const interval = setInterval(async () => {
      const resp = await fetch(`${API_URL}/api/result/${id}`)
      const data = await resp.json()
      if (data.result_url) {
        setStreamUrl(`${API_URL}/api/stream/${id}`)
        clearInterval(interval)
      }
    }, 2000)
  }

  return (
    <div>
      <h2>Live RTSP Stream</h2>
      <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="rtsp://example.com/stream" />
      <button onClick={handleSubmit}>Start Processing</button>
      {streamUrl && <img src={streamUrl} alt="Processed Stream" />}
    </div>
  )
}
