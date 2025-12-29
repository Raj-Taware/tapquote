import { useState } from 'react'
import './App.css'

// API URL - uses env variable in production, proxy in development
const API_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [jobDescription, setJobDescription] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [quote, setQuote] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [downloading, setDownloading] = useState(false)

  const handleGenerateQuote = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }

    setLoading(true)
    setError(null)
    setQuote(null)

    try {
      const response = await fetch(`${API_URL}/generate-quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_description: jobDescription,
          customer_name: customerName || 'Customer',
        }),
      })

      const data = await response.json()

      if (data.success) {
        setQuote(data.quote)
      } else {
        setError(data.error || 'Failed to generate quote')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!quote) return

    setDownloading(true)

    try {
      const response = await fetch(`${API_URL}/download-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quote }),
      })

      if (!response.ok) throw new Error('Failed to generate PDF')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `quote_${customerName || 'customer'}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError('Failed to download PDF')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="min-h-screen p-6 md:p-10">
      {/* Header */}
      <header className="max-w-6xl mx-auto mb-10">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">TapQuote</h1>
            <p className="text-slate-400 text-sm">AI-Powered Electrical Quotes</p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
        {/* Input Panel */}
        <section className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Job Details
          </h2>

          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Customer Name (Optional)
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="e.g., John Smith"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Describe the electrical work needed...&#10;&#10;Example: Install 4 LED downlights in the kitchen, supply and fit new Clipsal double GPO in the bedroom, and run a new 20A circuit for the pool pump."
                rows={8}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
              />
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerateQuote}
              disabled={loading}
              className="w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold rounded-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none btn-glow"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5 spinner" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                    <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="4" className="opacity-75" />
                  </svg>
                  Generating Quote...
                </span>
              ) : (
                'Generate Quote'
              )}
            </button>
          </div>
        </section>

        {/* Quote Preview Panel */}
        <section className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Quote Preview
          </h2>

          {!quote ? (
            <div className="flex flex-col items-center justify-center h-80 text-slate-500">
              <svg className="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>Enter a job description and generate a quote</p>
            </div>
          ) : (
            <div className="space-y-4 fade-in">
              {/* Customer & Summary */}
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <p className="text-sm text-slate-400">Customer</p>
                <p className="text-white font-medium">{quote.customer_name}</p>
                <p className="text-sm text-slate-400 mt-3">Job Summary</p>
                <p className="text-slate-300 text-sm">{quote.job_summary}</p>
              </div>

              {/* Line Items */}
              <div className="space-y-2">
                <p className="text-sm text-slate-400 mb-2">Line Items</p>
                {quote.items?.map((item, index) => (
                  <div key={index} className="p-3 bg-slate-800/30 rounded-lg quote-item">
                    <div className="flex justify-between items-start gap-4">
                      <div className="flex-1">
                        <p className="text-white text-sm">
                          {item.description}
                          {item.is_estimate && (
                            <span className="ml-2 text-xs text-amber-400">(Estimate)</span>
                          )}
                        </p>
                        <p className="text-slate-500 text-xs mt-1">
                          Qty: {item.qty} × ${item.unit_material_cost?.toFixed(2)} + {item.estimated_hours}hr labor
                        </p>
                      </div>
                      <p className="text-emerald-400 font-semibold">
                        ${item.line_total?.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="p-4 bg-gradient-to-r from-slate-800/50 to-slate-800/30 rounded-lg space-y-2">
                <div className="flex justify-between text-slate-400 text-sm">
                  <span>Subtotal</span>
                  <span>${quote.subtotal?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-400 text-sm">
                  <span>GST (10%)</span>
                  <span>${quote.tax?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-white font-bold text-lg pt-2 border-t border-slate-700">
                  <span>Total</span>
                  <span className="text-emerald-400">${quote.grand_total?.toFixed(2)}</span>
                </div>
              </div>

              {/* Download Button */}
              <button
                onClick={handleDownloadPDF}
                disabled={downloading}
                className="w-full py-3 px-6 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-semibold rounded-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 btn-glow"
              >
                {downloading ? (
                  <>
                    <svg className="w-5 h-5 spinner" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                      <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="4" className="opacity-75" />
                    </svg>
                    Generating PDF...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Download PDF
                  </>
                )}
              </button>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto mt-10 text-center text-slate-500 text-sm">
        <p>Powered by AI • Labor Rate: $85/hr • Material Markup: 20%</p>
      </footer>
    </div>
  )
}

export default App
