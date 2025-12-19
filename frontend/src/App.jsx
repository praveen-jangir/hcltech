import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { LayoutDashboard, Home, Activity, X, CheckCircle, AlertCircle, UploadCloud, Send } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('Home')
  const [health, setHealth] = useState('Checking backend...')

  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)

  const [chatQuery, setChatQuery] = useState('')
  const [chatHistory, setChatHistory] = useState([
    { type: 'bot', text: "Hello! I've analyzed your uploaded documents. Ask me anything!" }
  ])
  const chatWindowRef = useRef(null)

  const [modal, setModal] = useState({ show: false, message: '', type: 'success' })

  useEffect(() => {
    axios.get('/api/health')
      .then(res => setHealth(res.data.message))
      .catch(err => setHealth('Backend offline'))
  }, [])

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight
    }
  }, [chatHistory])

  const handleUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setIsUploading(true)
    setUploadProgress(0)

    axios.post('/api/upload', formData, {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(percentCompleted)
      }
    })
      .then(res => {
        setModal({ show: true, message: res.data.message, type: 'success' })
        setIsUploading(false)
      })
      .catch(err => {
        setModal({ show: true, message: 'Upload failed. Please try again.', type: 'error' })
        setIsUploading(false)
      })
  }

  const handleSend = () => {
    if (!chatQuery.trim()) return

    const userMsg = { type: 'user', text: chatQuery }
    setChatHistory(prev => [...prev, userMsg])
    const currentQuery = chatQuery
    setChatQuery('')

    axios.post('/api/ask', { query: currentQuery })
      .then(res => {
        const botMsg = {
          type: 'bot',
          internal: res.data.internal,
          external: res.data.external
        }
        setChatHistory(prev => [...prev, botMsg])
      })
      .catch(err => {
        const errorMsg = { type: 'error', text: "Sorry, I encountered an error answering that." }
        setChatHistory(prev => [...prev, errorMsg])
        console.error(err)
      })
  }

  const closeModal = () => setModal({ ...modal, show: false })

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-items">
          <button onClick={() => setActiveTab('Home')} className={activeTab === 'Home' ? 'active' : ''}>
            <Home size={20} /> Home
          </button>
          <button onClick={() => setActiveTab('Dashboard')} className={activeTab === 'Dashboard' ? 'active' : ''}>
            <LayoutDashboard size={20} /> Dashboard
          </button>
          <button onClick={() => setActiveTab('Predictions')} className={activeTab === 'Predictions' ? 'active' : ''}>
            <Activity size={20} /> Predictions
          </button>
        </div>
        <div className="nav-status">
          <span className="status-badge">{health}</span>
        </div>
      </nav>

      <main className="content">
        {activeTab === 'Home' && (
          <div className="home-view">
            <div className="hero-section">
              <div className="hero-content">
                <h1>Excellent Mirror</h1>
                <p>Advanced AI Solution | HCL Tech Hackathon</p>
                <div className="hero-image-container">
                  <img src="/assets/images/team.png" alt="Team Hero" className="hero-img" />
                </div>
              </div>
            </div>

            <div className="architecture-section">
              <h2>System Architecture</h2>
              <img src="/assets/images/architecture.jpg" alt="Architecture" className="arch-img" />
            </div>
          </div>
        )}

        {activeTab === 'Dashboard' && (
          <div className="dashboard-view">
            <div className="dashboard-header">
              <h1>Rag based document assistant</h1>
              <p className="subtitle">Upload documents and ask questions instantly.</p>
            </div>

            <div className="rag-container">
              <div className="upload-section">
                <div className="section-title">
                  <UploadCloud size={24} /> Upload Documents
                </div>

                <div className="upload-box">
                  <input type="file" id="fileInput" onChange={handleUpload} />
                  <div className="upload-text">Drag & Drop or Click to Upload</div>
                  <div className="upload-hint">Supported: PDF, IMG, DOC, TXT</div>
                </div>
                {isUploading && (
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                    </div>
                    <span className="progress-text">{uploadProgress}% Uploading...</span>
                  </div>
                )}
              </div>


              <div className="chat-section">
                <div className="section-title">
                  <h3>Ask any thing from files</h3>
                </div>
                <div className="chat-window" ref={chatWindowRef}>
                  {chatHistory.map((msg, index) => (
                    <div key={index} className={`message-wrapper ${msg.type}`}>
                      {msg.type === 'user' ? (
                        <div className="user-message card-shadow">
                          {msg.text}
                        </div>
                      ) : msg.type === 'error' ? (
                        <div className="error-message">{msg.text}</div>
                      ) : (
                        <div className="comparison-container">
                          <div className="model-card internal-model">
                            <div className="model-header">
                              <span className="badge internal">⚡ Internal Model</span>
                            </div>
                            <div className="model-body">
                              {msg.internal?.answer || "No response"}
                            </div>
                            {msg.internal?.metrics && (
                              <div className="metrics-box">
                                <div className="metrics-grid">
                                  <span title="Cosine">Cosine: {msg.internal.metrics.cosine_similarity}</span>
                                  <span title="ROUGE">ROUGE: {msg.internal.metrics.rouge_1}</span>
                                  <span title="BLEU">BLEU: {msg.internal.metrics.bleu}</span>
                                  <span title="MRR">MRR: {msg.internal.metrics.mrr}</span>
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="model-card external-model">
                            <div className="model-header">
                              <span className="badge external">runing in gpu model name is deberta-v3-large</span>
                            </div>
                            <div className="model-body">
                              {msg.external?.answer || "No response received."}
                            </div>

                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                <div className="chat-input-area">
                  <input
                    type="text"
                    placeholder="Type your query..."
                    value={chatQuery}
                    onChange={(e) => setChatQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  />
                  <button className="send-btn" onClick={handleSend}>
                    <Send size={18} /> Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {modal.show && (
        <div className="modal-overlay">
          <div className={`modal-content ${modal.type}`}>
            <button className="modal-close" onClick={closeModal}><X size={20} /></button>
            <div className="modal-icon">
              {modal.type === 'success' ? <CheckCircle size={48} /> : <AlertCircle size={48} />}
            </div>
            <h3>{modal.type === 'success' ? 'Success!' : 'Error'}</h3>
            <p>{modal.message}</p>
            <button className="modal-btn" onClick={closeModal}>Close</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
