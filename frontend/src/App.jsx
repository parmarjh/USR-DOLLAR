import { useState, useEffect, useCallback } from 'react'
import './index.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [agents, setAgents] = useState([])
  const [stats, setStats] = useState(null)
  const [config, setConfig] = useState(null)
  const [documents, setDocuments] = useState([])
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState('analyze')
  const [result, setResult] = useState(null)
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [toast, setToast] = useState(null)
  const [activeStep, setActiveStep] = useState(null)
  const [dragging, setDragging] = useState(false)

  // Toast helper
  const showToast = useCallback((message, isError = false) => {
    setToast({ message, isError })
    setTimeout(() => setToast(null), 4000)
  }, [])

  // Fetch initial data
  useEffect(() => {
    fetchAgents()
    fetchStats()
    fetchConfig()
    fetchDocuments()
  }, [])

  async function fetchAgents() {
    try {
      const res = await fetch(`${API_BASE}/api/agents`)
      const data = await res.json()
      setAgents(data.agents || [])
    } catch (e) {
      console.error('Cannot reach backend:', e)
    }
  }

  async function fetchStats() {
    try {
      const res = await fetch(`${API_BASE}/api/stats`)
      setStats(await res.json())
    } catch (e) { /* backend not running */ }
  }

  async function fetchConfig() {
    try {
      const res = await fetch(`${API_BASE}/api/config`)
      setConfig(await res.json())
    } catch (e) { /* backend not running */ }
  }

  async function fetchDocuments() {
    try {
      const res = await fetch(`${API_BASE}/api/documents`)
      const data = await res.json()
      setDocuments(data.documents || [])
    } catch (e) { /* backend not running */ }
  }

  // Upload PDF
  async function handleUpload(file) {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Only PDF files are accepted', true)
      return
    }
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData })
      if (!res.ok) throw new Error('Upload failed')
      showToast(`✅ Uploaded: ${file.name}`)
    } catch (e) {
      showToast(`Upload failed: ${e.message}`, true)
    }
    setUploading(false)
  }

  // Ingest documents
  async function handleIngest() {
    setIngesting(true)
    setActiveStep('librarian')
    try {
      const res = await fetch(`${API_BASE}/api/ingest`, { method: 'POST' })
      if (!res.ok) throw new Error('Ingest failed')
      const data = await res.json()
      setActiveStep('researcher')
      setTimeout(() => {
        setActiveStep(null)
        showToast(`✅ Ingested ${data.total_files} files, ${data.total_chunks} chunks`)
        fetchStats()
        fetchDocuments()
        fetchAgents()
      }, 800)
    } catch (e) {
      showToast(`Ingest failed: ${e.message}`, true)
      setActiveStep(null)
    }
    setIngesting(false)
  }

  // Query system
  async function handleQuery(e) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setResult(null)
    setSources([])
    setActiveStep('researcher')
    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, mode, top_k: 3 }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Query failed')
      }
      setActiveStep('analyst')
      const data = await res.json()
      setTimeout(() => {
        setResult(data.answer)
        setSources(data.sources || [])
        setActiveStep(null)
      }, 500)
    } catch (e) {
      showToast(e.message, true)
      setActiveStep(null)
    }
    setLoading(false)
  }

  // Drag & drop
  function onDragOver(e) { e.preventDefault(); setDragging(true) }
  function onDragLeave() { setDragging(false) }
  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  const modes = [
    { id: 'analyze', label: '📊 Analyze', desc: 'Deep analysis' },
    { id: 'summarize', label: '📝 Summarize', desc: 'Key points' },
    { id: 'compare', label: '⚖️ Compare', desc: 'Side-by-side' },
    { id: 'develop', label: '💡 Develop', desc: 'Action plan' },
  ]

  const roleClass = (role) => {
    if (role === 'librarian') return 'librarian'
    if (role === 'researcher') return 'researcher'
    if (role === 'analyst') return 'analyst'
    return ''
  }

  return (
    <>
      {/* HEADER */}
      <header className="header">
        <div className="header-left">
          <div className="header-logo">🤖</div>
          <h1>
            Multi-Agent Research System
            <br />
            <span>Librarian → Researcher → Analyst</span>
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          {config && (
            <div className="header-badge">
              🔌 {config.llm_provider?.toUpperCase()} — {config.llm_model}
            </div>
          )}
          <div className="header-badge">
            <span className="dot"></span>
            {stats ? `${stats.total_vectors} vectors` : 'Connecting...'}
          </div>
        </div>
      </header>

      <div className="app-container">
        {/* AGENT CARDS */}
        <div className="section-title">Agent Setup Table</div>
        <div className="agents-grid">
          {(agents.length > 0 ? agents : [
            { id: 1, emoji: '📚', name: 'The Librarian', role: 'librarian', description: 'Scans PDFs, extracts text, indexes metadata', capabilities: ['PDF extraction', 'Chunking', 'SQLite indexing'], status: 'ready' },
            { id: 2, emoji: '🔍', name: 'The Researcher', role: 'researcher', description: 'Semantic search for accurate context retrieval', capabilities: ['Embeddings', 'FAISS search', 'Top-K matching'], status: 'ready' },
            { id: 3, emoji: '🧠', name: 'The Analyst', role: 'analyst', description: 'Generates structured insights via LLM', capabilities: ['OpenRouter', '4 analysis modes', 'Reports'], status: 'ready' },
          ]).map(agent => (
            <div key={agent.id} className={`agent-card ${roleClass(agent.role)}`}>
              <div className="agent-header">
                <div className="agent-emoji">{agent.emoji}</div>
                <div>
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-role">{agent.role}</div>
                </div>
              </div>
              <div className="agent-desc">{agent.description}</div>
              <div className="agent-caps">
                {(agent.capabilities || []).slice(0, 4).map((cap, i) => (
                  <span key={i} className="agent-cap-tag">{cap}</span>
                ))}
              </div>
              <div className={`agent-status ${activeStep === agent.role ? 'working' : ''}`}>
                {activeStep === agent.role ? (
                  <><span className="spinner" style={{ width: 12, height: 12 }}></span> Working...</>
                ) : (
                  <>🟢 Ready</>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* PIPELINE FLOW */}
        <div className="pipeline">
          {['📄 PDFs', '📚 Librarian', '🔍 Researcher', '🧠 Analyst', '📊 Insights'].map((step, i, arr) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className={`pipeline-step ${activeStep && step.toLowerCase().includes(activeStep) ? 'active' : ''}`}>
                {step}
              </span>
              {i < arr.length - 1 && <span className="pipeline-arrow">→</span>}
            </span>
          ))}
        </div>

        {/* STATS BAR */}
        <div className="stats-bar">
          <div className="stat-card">
            <div className="stat-value">{stats?.total_documents ?? 0}</div>
            <div className="stat-label">Documents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats?.total_vectors ?? 0}</div>
            <div className="stat-label">Vectors</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats?.vector_dimension ?? 384}</div>
            <div className="stat-label">Dimensions</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{config?.llm_provider?.toUpperCase() ?? '—'}</div>
            <div className="stat-label">LLM Provider</div>
          </div>
        </div>

        {/* MAIN GRID */}
        <div className="main-grid">
          {/* LEFT: Upload + Query */}
          <div>
            {/* Upload Panel */}
            <div className="panel" style={{ marginBottom: 24 }}>
              <div className="panel-title">📤 Upload & Ingest PDFs</div>
              <div
                className={`upload-area ${dragging ? 'dragging' : ''}`}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
                onClick={() => document.getElementById('file-input').click()}
              >
                <div className="upload-icon">📄</div>
                <div className="upload-text">
                  {uploading ? 'Uploading...' : 'Drop PDF here or click to browse'}
                </div>
                <div className="upload-hint">Supports .pdf files</div>
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf"
                  hidden
                  onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
                />
              </div>
              <button
                className="submit-btn secondary"
                onClick={handleIngest}
                disabled={ingesting}
              >
                {ingesting ? <><span className="spinner"></span> Processing...</> : '🚀 Ingest All PDFs'}
              </button>
            </div>

            {/* Query Panel */}
            <div className="panel">
              <div className="panel-title">🔍 Query Your Research</div>
              <form onSubmit={handleQuery}>
                <div className="query-input-wrapper">
                  <textarea
                    className="query-input"
                    placeholder="Ask anything about your documents...&#10;e.g. What are the main architectural patterns?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
                <div className="mode-selector">
                  {modes.map(m => (
                    <button
                      key={m.id}
                      type="button"
                      className={`mode-btn ${mode === m.id ? 'active' : ''}`}
                      onClick={() => setMode(m.id)}
                      title={m.desc}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
                <button className="submit-btn" type="submit" disabled={loading || !query.trim()}>
                  {loading ? <><span className="spinner"></span> Analyzing...</> : '🧠 Run Agent Pipeline'}
                </button>
              </form>
            </div>
          </div>

          {/* RIGHT: Results */}
          <div>
            <div className="panel" style={{ minHeight: 400 }}>
              <div className="panel-title">📊 Results — {mode.charAt(0).toUpperCase() + mode.slice(1)} Mode</div>
              {result ? (
                <>
                  <div className="result-container has-content">{result}</div>
                  {sources.length > 0 && (
                    <>
                      <div style={{ marginTop: 20, fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>
                        📎 Sources ({sources.length})
                      </div>
                      <div className="sources-list">
                        {sources.map((s, i) => (
                          <div key={i} className="source-item">
                            <div className="source-meta">
                              <span className="source-rank">#{s.rank}</span>
                              <span className="source-score">Score: {s.score}</span>
                            </div>
                            <div className="source-text">{s.text}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </>
              ) : loading ? (
                <div className="empty-state">
                  <div className="spinner" style={{ width: 32, height: 32, marginBottom: 16 }}></div>
                  <p>Agents are working on your query...</p>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🔬</div>
                  <p>Upload PDFs, ingest them, then ask a question.<br />The 3 agents will work together to find answers.</p>
                </div>
              )}
            </div>

            {/* Documents Table */}
            {documents.length > 0 && (
              <div className="panel" style={{ marginTop: 24 }}>
                <div className="panel-title">📚 Indexed Documents ({documents.length})</div>
                <table className="docs-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Filename</th>
                      <th>Pages</th>
                      <th>Chunks</th>
                      <th>Indexed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc, i) => (
                      <tr key={i}>
                        <td>{doc.id}</td>
                        <td style={{ color: 'var(--accent-purple)' }}>{doc.filename}</td>
                        <td>{doc.page_count}</td>
                        <td>{doc.chunk_count}</td>
                        <td>{doc.indexed_at?.split('.')[0]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* TOAST */}
      {toast && (
        <div className={`toast ${toast.isError ? 'error' : ''}`}>
          {toast.message}
        </div>
      )}
    </>
  )
}

export default App
