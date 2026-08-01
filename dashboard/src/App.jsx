import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import { Activity, BrainCircuit, Box, Shield, Zap, Info } from 'lucide-react'

const API_BASE = `http://${window.location.hostname}:8001`

function App() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const runDemoAnalysis = async () => {
    setLoading(true)
    setError('')
    try {
      // Mock data for demo API call
      const payload = {
        name: "God-Mode Demo",
        description: "Testing API and Dashboard",
        mode: "advanced",
        use_ai: false,
        factors: [
          { name: "Cost", weight: 0.4, maximize: false },
          { name: "Performance", weight: 0.6, maximize: true }
        ],
        options: [
          {
            name: "Option A",
            description: "Standard choice",
            variables: {
              "Cost": { distribution: "normal", params: [100, 10] },
              "Performance": { distribution: "normal", params: [80, 5] }
            }
          },
          {
            name: "Option B",
            description: "High risk, high reward",
            variables: {
              "Cost": { distribution: "normal", params: [150, 30] },
              "Performance": { distribution: "normal", params: [120, 20] }
            }
          }
        ]
      }
      const res = await axios.post(`${API_BASE}/analyze`, payload)
      setResults(res.data)
    } catch (err) {
      const errorData = err.response?.data?.detail || err.message
      setError(typeof errorData === 'string' ? errorData : JSON.stringify(errorData))
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
          <div className="loader" style={{ width: '48px', height: '48px', marginBottom: '1rem', borderTopColor: '#c084fc' }}></div>
          <h3 style={{ background: 'linear-gradient(135deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Running God-Mode Simulations...</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Calculating Monte Carlo, Game Theory, and ROA metrics.</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="glass-panel" style={{ borderLeft: '4px solid var(--danger-color)' }}>
          <div className="card-title" style={{ color: 'var(--danger-color)' }}><Info size={20} /> Error Analysis</div>
          <p>{error}</p>
        </div>
      )
    }

    if (!results) {
      return (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <BrainCircuit size={64} style={{ color: 'var(--accent-color)', marginBottom: '1rem' }} />
          <h2>Decision Engine Ready</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 2rem auto' }}>
            The Hybrid Rust/Python framework is online. Connect to the API to run Bayesian Networks, Real Options Analysis, and Game Theory calculations in microseconds.
          </p>
          <button className="btn" onClick={runDemoAnalysis}>
            <Zap size={18} /> Run Demo Simulation
          </button>
        </div>
      )
    }

    // Format data for charts
    const mcData = Object.entries(results.mc_results).map(([name, stats]) => ({
      name,
      Mean: stats.mean_score,
      Success: stats.success_rate * 100
    }))

    const topsisData = Object.entries(results.topsis_scores).map(([name, score]) => ({
      name,
      Score: score
    }))

    return (
      <div className="grid-layout">
        {/* Recommendation Panel */}
        <div className="glass-panel" style={{ gridColumn: '1 / -1', background: 'linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9))', borderTop: '2px solid var(--accent-color)' }}>
          <div className="card-title">Recommendation</div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div className="stat-value" style={{ background: 'linear-gradient(135deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                {results.winner || "Tie"}
              </div>
              <div className="stat-label">Optimal Choice via F-TOPSIS Distance</div>
            </div>
            {results.future_metrics?.game_theory?.nash_equilibrium && (
              <div style={{ textAlign: 'right' }}>
                <div style={{ color: 'var(--success-color)', fontWeight: 'bold' }}>Nash Equilibrium: Stable</div>
                <div className="stat-label">Game Theory Verified</div>
              </div>
            )}
          </div>
        </div>

        {/* Monte Carlo Results */}
        <div className="glass-panel">
          <div className="card-title"><Activity size={20} /> Monte Carlo Expectations</div>
          <div style={{ height: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mcData}>
                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip contentStyle={{ background: 'var(--bg-color)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
                <Bar dataKey="Mean" fill="var(--accent-color)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* TOPSIS Scores */}
        <div className="glass-panel">
          <div className="card-title"><Shield size={20} /> TOPSIS Ranking</div>
          <div style={{ height: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart outerRadius={90} data={topsisData}>
                <PolarGrid stroke="var(--border-color)" />
                <PolarAngleAxis dataKey="name" stroke="var(--text-secondary)" />
                <PolarRadiusAxis angle={30} domain={[0, 1]} stroke="var(--text-secondary)" />
                <Radar name="Score" dataKey="Score" stroke="#c084fc" fill="#c084fc" fillOpacity={0.6} />
                <Tooltip contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: '8px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Advanced Metrics */}
        <div className="glass-panel" style={{ gridColumn: '1 / -1' }}>
          <div className="card-title"><Box size={20} /> Advanced Metrics (God-Mode)</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {results.future_metrics?.roa && (
              <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                <div className="stat-label">Real Options Value (ROA)</div>
                <div className="stat-value" style={{ fontSize: '1.5rem' }}>${results.future_metrics.roa?.call_option_value?.toFixed(2) || '0.00'}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Volatility: {(results.future_metrics.roa?.volatility * 100).toFixed(1)}%</div>
              </div>
            )}
            
            {Object.entries(mcData).map(([i, opt]) => (
              <div key={i} style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                <div className="stat-label">{opt.name} Success Rate</div>
                <div className="stat-value" style={{ fontSize: '1.5rem', color: opt.Success > 50 ? 'var(--success-color)' : 'var(--danger-color)' }}>
                  {opt.Success.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <header className="dashboard-header">
        <h1>Lumina Decision Maker</h1>
        <div>
          <span style={{ padding: '4px 12px', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-color)', borderRadius: '16px', fontSize: '0.875rem', fontWeight: 600 }}>
            v3.0 Hybrid Engine
          </span>
        </div>
      </header>
      
      <main className="dashboard-container">
        {renderContent()}
      </main>
    </>
  )
}

export default App
