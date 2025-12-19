import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { LayoutDashboard, Home, Activity, X, CheckCircle, AlertCircle, UploadCloud, Send } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('Home')
  const [health, setHealth] = useState('Checking backend...')

  // Upload State
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)

  // Chat State
  const [chatQuery, setChatQuery] = useState('')
  const [chatHistory, setChatHistory] = useState([
    { type: 'bot', text: "Hello! I've analyzed your uploaded documents. Ask me anything!" }
  ])
  const chatWindowRef = useRef(null)

  // Modal State
  const [modal, setModal] = useState({ show: false, message: '', type: 'success' })

  useEffect(() => {
    axios.get('/api/health')
      .then(res => setHealth(res.data.message))
      .catch(err => setHealth('Backend offline ⚠️'))
  }, [])

  // Auto-scroll chat
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

    // Add User Message
    const userMsg = { type: 'user', text: chatQuery }
    setChatHistory(prev => [...prev, userMsg])
    const currentQuery = chatQuery
    setChatQuery('') // Clear input

    // Call API
    axios.post('/api/ask', { query: currentQuery })
      .then(res => {
        const botMsg = { type: 'bot', text: res.data.answer }
        setChatHistory(prev => [...prev, botMsg])
      })
      .catch(err => {
        const errorMsg = { type: 'bot', text: "Sorry, I encountered an error answering that." }
        setChatHistory(prev => [...prev, errorMsg])
        console.error(err)
      })
  }

  const closeModal = () => setModal({ ...modal, show: false })

  return (
    <div className="app-container">
      {/* Navigation */}
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

      {/* Content */}
      <main className="content">
        {activeTab === 'Home' && (
          <div className="home-view">
            <div className="hero-section">
              <div className="hero-content">
                <h1>Excellent Mirror 🔮</h1>
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
              <h1>RAG Document Assistant 🤖</h1>
              <p className="subtitle">Upload documents and ask questions instantly.</p>
            </div>

            <div className="rag-container">
              {/* File Uploader */}
              <div className="upload-section">
                <div className="section-title">
                  <UploadCloud size={24} /> Upload Documents
                </div>

                <div className="upload-box">
                  <input type="file" id="fileInput" onChange={handleUpload} />
                  <div className="upload-icon">📂</div>
                  <div className="upload-text">Drag & Drop or Click to Upload</div>
                  <div className="upload-hint">Supported: PDF, IMG, DOC, TXT</div>
                </div>

                {/* Progress Bar */}
                {isUploading && (
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                    </div>
                    <span className="progress-text">{uploadProgress}% Uploading...</span>
                  </div>
                )}
              </div>

              {/* Chat Interface */}
              <div className="chat-section">
                <div className="section-title">
                  <h3>💬 Ask AI</h3>
                </div>
                <div className="chat-window" ref={chatWindowRef}>
                  {chatHistory.map((msg, index) => (
                    <div key={index} className={`message ${msg.type === 'user' ? 'user-message' : 'bot-message'}`}>
                      {msg.text}
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

      {/* Custom Modal */}
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
