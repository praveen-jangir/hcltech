import { useState, useEffect } from 'react'
import axios from 'axios'
import { LayoutDashboard, Home, Info, Activity } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('Home')
  const [health, setHealth] = useState('Checking backend...')

  useEffect(() => {
    axios.get('/api/health')
      .then(res => setHealth(res.data.message))
      .catch(err => setHealth('Backend offline ⚠️'))
  }, [])

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
            <h1>RAG Document Assistant 🤖</h1>
            <p className="subtitle">Upload documents and ask questions instantly.</p>

            <div className="rag-container">
              {/* File Uploader */}
              <div className="upload-section">
                <h3>📂 Upload Documents</h3>
                <div className="upload-box">
                  <input type="file" id="fileInput" onChange={(e) => {
                    const file = e.target.files[0];
                    if (!file) return;

                    const formData = new FormData();
                    formData.append('file', file);

                    axios.post('/api/upload', formData)
                      .then(res => alert(res.data.message))
                      .catch(err => alert('Upload failed'));
                  }} />
                  <p>Supported: PDF, IMG, DOC, PPT, XLS, CSV, TXT</p>
                </div>
              </div>

              {/* Chat Interface */}
              <div className="chat-section">
                <h3>💬 Ask AI</h3>
                <div className="chat-window">
                  {/* Message History Placeholder */}
                  <div className="message bot-message">
                    Hello! I've analyzed your 5 documents. Ask me anything!
                  </div>
                </div>
                <div className="chat-input-area">
                  <input type="text" placeholder="Type your query..." onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const query = e.target.value;
                      if (!query) return;

                      // Optimistic UI update could go here
                      axios.post('/api/ask', { query })
                        .then(res => alert(`AI Answer: ${res.data.answer}`))
                        .catch(err => console.error(err));

                      e.target.value = '';
                    }
                  }} />
                  <button className="send-btn">Send</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
