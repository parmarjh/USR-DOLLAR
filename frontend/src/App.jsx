import React, { useState, useEffect, useRef } from 'react';

// API Configuration
const API_BASE = 'http://localhost:8000';

const App = () => {
  // State
  const [agents, setAgents] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState(null);
  const [godReport, setGodReport] = useState(null);
  
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('analyze');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [sources, setSources] = useState([]);
  
  const [uploading, setUploading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [toast, setToast] = useState(null);
  
  const fileInputRef = useRef(null);

  // Fetch initial data
  useEffect(() => {
    fetchData();
    checkGodReport();
    
    // Check god report every 30 seconds
    const interval = setInterval(checkGodReport, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkGodReport = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/god-mode-report`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.exists) setGodReport(data.content);
    } catch (e) {
      // Silently fail if not found
    }
  };

  const fetchData = async () => {
    try {
      const [agentsRes, docsRes, statsRes, configRes] = await Promise.all([
        fetch(`${API_BASE}/api/agents`),
        fetch(`${API_BASE}/api/documents`),
        fetch(`${API_BASE}/api/stats`),
        fetch(`${API_BASE}/api/config`)
      ]);

      const agentsData = await agentsRes.json();
      const docsData = await docsRes.json();
      const statsData = await statsRes.json();
      const configData = await configRes.json();

      setAgents(agentsData.agents);
      setDocuments(docsData.documents);
      setStats(statsData);
      setConfig(configData);
    } catch (error) {
      console.error('Error fetching data:', error);
      showToast('Backend connection failed', 'error');
    }
  };

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setSources([]);

    try {
      const response = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, mode, top_k: 5 })
      });

      if (!response.ok) throw new Error('Query failed');

      const data = await response.json();
      setResult(data.answer);
      setSources(data.sources);
      showToast('Insights Generated');
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Upload failed');
      
      showToast(`File uploaded successfully`);
      fetchData();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleIngest = async () => {
    setIngesting(true);
    try {
      const response = await fetch(`${API_BASE}/api/ingest`, { method: 'POST' });
      if (!response.ok) throw new Error('Ingestion failed');
      
      const data = await response.json();
      showToast(`Processed ${data.total_files} documents`);
      fetchData();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setIngesting(false);
    }
  };

  const formatMarkdown = (text) => {
    if (!text) return text;
    return text.split('\n').map((line, i) => {
      if (line.startsWith('# ')) return <h1 key={i} style={{ color: 'var(--accent-purple)', marginBottom: '15px' }}>{line.replace('# ', '')}</h1>;
      if (line.startsWith('## ')) return <h2 key={i} style={{ color: 'var(--accent-cyan)', marginTop: '20px', marginBottom: '10px' }}>{line.replace('## ', '')}</h2>;
      if (line.startsWith('### ')) return <h3 key={i} style={{ color: 'var(--text-primary)', marginTop: '15px', marginBottom: '5px' }}>{line.replace('### ', '')}</h3>;
      if (line.startsWith('- ') || line.startsWith('* ')) return <li key={i} style={{ marginLeft: '20px', marginBottom: '5px' }}>{line.substring(2)}</li>;
      if (line.trim() === '---') return <hr key={i} style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '20px 0' }} />;
      if (line.trim() === '') return <div key={i} style={{ height: '10px' }} />;
      return <p key={i} style={{ marginBottom: '10px' }}>{line}</p>;
    });
  };

  return (
    <div className="app">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast ${toast.type === 'error' ? 'error' : ''}`}>
          {toast.message}
        </div>
      )}

      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="header-logo">🤖</div>
          <h1>Multi-Agent <span>Research System</span></h1>
        </div>
        <div className="header-badge">
          <div className="dot"></div>
          {config ? `${config.llm_provider.toUpperCase()} (${config.llm_model})` : 'System Offline'}
        </div>
      </header>

      <main className="app-container">
        {/* God Mode Banner */}
        {godReport && (
          <section className="panel" style={{ marginBottom: '40px', border: '1px solid gold', background: 'rgba(255, 215, 0, 0.05)' }}>
            <div className="panel-title" style={{ color: 'gold' }}>⚡ GOD MODE MASTER REPORT AVAILABLE</div>
            <div className="result-container has-content" style={{ maxHeight: '400px', border: '1px solid rgba(255, 215, 0, 0.2)' }}>
              {formatMarkdown(godReport)}
            </div>
            <button className="submit-btn" style={{ marginTop: '15px', background: 'linear-gradient(135deg, #FFD700, #FFA500)', color: 'black' }} onClick={() => fetchData()}>
              Refresh Global Knowledge Memory
            </button>
          </section>
        )}

        {/* Agents Status */}
        <section>
          <div className="section-title">Active AI Agents</div>
          <div className="agents-grid">
            {agents.map(agent => (
              <div key={agent.id} className={`agent-card ${agent.role}`}>
                <div className="agent-header">
                  <div className="agent-emoji">{agent.emoji}</div>
                  <div>
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-role">{agent.role}</div>
                  </div>
                </div>
                <p className="agent-desc">{agent.description}</p>
                <div className="agent-caps">
                  {agent.capabilities.map((cap, i) => (
                    <span key={i} className="agent-cap-tag">{cap}</span>
                  ))}
                </div>
                <div className={`agent-status ${agent.status !== 'ready' ? 'working' : ''}`}>
                  {agent.status === 'ready' ? '● System Standby' : '● Thinking...'}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Stats Bar */}
        <section className="stats-bar">
          <div className="stat-card">
            <div className="stat-value">{stats?.total_documents || 0}</div>
            <div className="stat-label">Documents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats?.total_vectors || 0}</div>
            <div className="stat-label">Total Vectors</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{config?.llm_provider || '—'}</div>
            <div className="stat-label">LLM Provider</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">3</div>
            <div className="stat-label">Active Agents</div>
          </div>
        </section>

        {/* Pipeline Visual */}
        <div className="pipeline">
          <div className={`pipeline-step ${ingesting ? 'active' : ''}`}>📚 Librarian</div>
          <div className="pipeline-arrow">→</div>
          <div className={`pipeline-step ${ingesting ? 'active' : ''}`}>🔍 Researcher</div>
          <div className="pipeline-arrow">→</div>
          <div className={`pipeline-step ${loading ? 'active' : ''}`}>🧠 Analyst</div>
        </div>

        {/* Main Content Grid */}
        <div className="main-grid">
          {/* Left: Input Panel */}
          <div className="panel">
            <div className="panel-title">🧠 Ask the Analyst</div>
            
            <div className="mode-selector">
              {['analyze', 'summarize', 'compare', 'develop'].map(m => (
                <button 
                  key={m} 
                  className={`mode-btn ${mode === m ? 'active' : ''}`}
                  onClick={() => setMode(m)}
                >
                  {m.toUpperCase()}
                </button>
              ))}
            </div>

            <form onSubmit={handleQuery}>
              <div className="query-input-wrapper">
                <textarea 
                  className="query-input"
                  placeholder="e.g., What are the core development ideas mentioned in these papers?"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <button className="submit-btn" disabled={loading || !query.trim()}>
                {loading ? <div className="spinner"></div> : 'Generate Insights'}
              </button>
            </form>

            <div style={{ marginTop: '30px' }}>
              <div className="panel-title">📄 Document Ingestion</div>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                style={{ display: 'none' }}
                accept=".pdf"
              />
              <div 
                className={`upload-area ${uploading ? 'dragging' : ''}`}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="upload-icon">📤</div>
                <div className="upload-text">{uploading ? 'Uploading...' : 'Click to Upload PDF'}</div>
                <div className="upload-hint">File will be added to research folder</div>
              </div>
              
              <button 
                className="submit-btn secondary" 
                onClick={handleIngest}
                disabled={ingesting || uploading}
              >
                {ingesting ? <div className="spinner"></div> : '✨ Ingest & Index Memory'}
              </button>
            </div>
          </div>

          {/* Right: Output Panel */}
          <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="panel-title">📊 Research Insights</div>
            
            <div className={`result-container ${result ? 'has-content' : ''}`}>
              {!result && !loading && (
                <div className="empty-state">
                  <div className="empty-icon">💡</div>
                  <p>Submit a query to see agent analysis here.</p>
                </div>
              )}
              {loading && (
                <div className="empty-state">
                  <div className="spinner" style={{ marginBottom: '15px' }}></div>
                  <p>Agents are processing context...</p>
                </div>
              )}
              {result && formatMarkdown(result)}
            </div>

            {sources.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <div className="panel-title" style={{ fontSize: '13px', marginBottom: '10px' }}>🔍 Retrieved Context</div>
                <div className="sources-list">
                  {sources.map((src, i) => (
                    <div key={i} className="source-item">
                      <div className="source-meta">
                        <span className="source-rank">#{src.rank} Source</span>
                        <span className="source-score">Match: {(src.score * 100).toFixed(1)}%</span>
                      </div>
                      <div className="source-text">"{src.text}..."</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Documents Section */}
        <section className="panel" style={{ marginTop: '24px' }}>
          <div className="panel-title">📚 Document Library</div>
          {documents.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table className="docs-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Pages</th>
                    <th>Chunks</th>
                    <th>Keywords</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{doc.filename}</td>
                      <td>{doc.page_count}</td>
                      <td>{doc.chunk_count}</td>
                      <td style={{ fontSize: '11px' }}>{doc.keywords}</td>
                      <td style={{ color: 'var(--accent-green)' }}>✅ Indexed</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <p>No documents indexed yet. Upload a PDF to begin.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default App;
