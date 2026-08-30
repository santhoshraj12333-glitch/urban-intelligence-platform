import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { getHealth } from '../services/api.js'

/**
 * components/Navbar.jsx
 * Purpose: Top navigation for the ONE common application — Overview /
 * Traffic / PWD / Events — plus a live indicator showing whether the app
 * is talking to the real FastAPI backend or running on mock/demo data.
 *
 * Connects to:
 * - src/App.jsx -> rendered on every route
 * - src/services/api.js -> getHealth() for the connection dot
 */
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK) === 'true'

const links = [
  { to: '/', label: 'Overview', end: true },
  { to: '/traffic', label: 'Traffic' },
  { to: '/pwd', label: 'PWD' },
  { to: '/events', label: 'Events' },
]

export default function Navbar() {
  const [connected, setConnected] = useState(null)

  useEffect(() => {
    if (USE_MOCK) return
    let cancelled = false
    getHealth().then((ok) => {
      if (!cancelled) setConnected(ok)
    })
    const interval = setInterval(async () => {
      const ok = await getHealth()
      if (!cancelled) setConnected(ok)
    }, 15000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const statusLabel = USE_MOCK
    ? 'DEMO DATA'
    : connected === null
    ? 'CHECKING…'
    : connected
    ? 'LIVE'
    : 'BACKEND UNAVAILABLE'

  const statusColor = USE_MOCK
    ? 'bg-signal-amber'
    : connected === null
    ? 'bg-slate-500'
    : connected
    ? 'bg-signal-green'
    : 'bg-signal-red'

  return (
    <nav className="sticky top-0 z-[1000] flex items-center justify-between border-b border-base-700 bg-base-950/95 px-6 py-3 backdrop-blur">
      <div className="flex items-center gap-8">
        <span className="font-display text-lg font-semibold tracking-tight text-slate-100">
          URBAN<span className="text-signal-cyan">INTEL</span>
        </span>
        <div className="flex gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-1.5 font-mono text-sm transition-colors ${
                  isActive
                    ? 'bg-base-700 text-slate-100'
                    : 'text-slate-400 hover:bg-base-800 hover:text-slate-200'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
        <span className={`h-2 w-2 rounded-full ${statusColor}`} />
        {statusLabel}
      </div>
    </nav>
  )
}
