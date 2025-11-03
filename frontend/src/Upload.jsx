import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState('')
  const [resultUrl, setResultUrl] = useState('')

  const handleUpload = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    const resp = await fetch(`${API_URL}/api/process/upload`, { method: 'POST', body: formData })
    const data = await resp.json()
    setJobId(data.job_id)
    pollStatus(data.job_id)
  }

  const pollStatus = async (id) => {
    const interval = setInterval(async () => {
      const resp = await fetch(`${API_URL}/api/result/${id}`)
      const data = await resp.json()
      setStatus(data.status)
      if (data.result_url && data.status === 'completed') {
        setResultUrl(`${API_URL}${data.result_url}`)
        clearInterval(interval)
      }
    }, 2000)
  }

  return (
    <div>
      <h2>Upload Video</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} accept="video/*" />
      <button onClick={handleUpload}>Process</button>
      {status && <p className="progress">Status: {status}</p>}
      {resultUrl && <video src={resultUrl} controls autoPlay />}
    </div>
  )
}
