import { useState } from 'react'
import Upload from './Upload.jsx'
import Live from './Live.jsx'

function App() {
  const [mode, setMode] = useState('upload')

  return (
    <div>
      <h1>Traffic Video Inference</h1>
      <button onClick={() => setMode('upload')}>Upload Mode</button>
      <button onClick={() => setMode('live')}>Live Mode</button>
      {mode === 'upload' ? <Upload /> : <Live />}
    </div>
  )
}

export default App
