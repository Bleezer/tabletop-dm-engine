import { NavLink } from 'react-router-dom'
import { useTheme, THEMES } from '../../context/ThemeContext'
import { useSaved } from '../../context/SavedResultsContext'

const NAV = [
  { to: '/',        icon: '⬡', label: 'Főoldal' },
  { to: '/location', icon: '🏰', label: 'Helyszín' },
  { to: '/npc',     icon: '⚔', label: 'NPC' },
  { to: '/saved',   icon: '📜', label: 'Mentések' },
]

export default function Sidebar() {
  const { themeId, setThemeId, themes } = useTheme()
  const { saved } = useSaved()
  const theme = themes[themeId]

  const otherThemeId = themeId === 'magus' ? 'starwars' : 'magus'
  const otherTheme   = themes[otherThemeId]

  return (
    <aside
      style={{
        width: '220px',
        minWidth: '220px',
        background: 'var(--th-surface)',
        borderRight: '1px solid var(--th-border)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        overflow: 'hidden',
      }}
    >
      {/* System brand */}
      <div
        style={{
          padding: '1.5rem 1rem 1rem',
          borderBottom: '1px solid var(--th-border)',
        }}
      >
        <div style={{ color: 'var(--th-gold)', fontSize: '1.5rem', textAlign: 'center' }}>
          {theme.icon}
        </div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.75rem',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: 'var(--th-gold)',
            textAlign: 'center',
            margin: '0.4rem 0 0.1rem',
          }}
        >
          {theme.label}
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.7rem',
            color: 'var(--th-muted)',
            textAlign: 'center',
            fontStyle: 'italic',
            margin: 0,
          }}
        >
          {theme.subtitle}
        </p>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '0.75rem 0.5rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {NAV.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              'sidebar-link' + (isActive ? ' active' : '')
            }
          >
            <span style={{ fontSize: '1rem', minWidth: '1.2rem' }}>{icon}</span>
            <span>{label}</span>
            {label === 'Mentések' && saved.length > 0 && (
              <span
                style={{
                  marginLeft: 'auto',
                  background: 'var(--th-accent)',
                  color: '#fff',
                  fontSize: '0.65rem',
                  padding: '1px 5px',
                  borderRadius: '9px',
                  fontFamily: 'var(--font-display)',
                }}
              >
                {saved.length}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Decorative rune section */}
      <div
        style={{
          padding: '0.5rem 1rem',
          textAlign: 'center',
          color: 'var(--th-border)',
          fontSize: '0.9rem',
          letterSpacing: '0.3em',
          fontFamily: 'var(--font-display)',
        }}
      >
        ᚱ ᚢ ᚾ ᛖ
      </div>

      {/* Theme switcher */}
      <div
        style={{
          padding: '0.75rem',
          borderTop: '1px solid var(--th-border)',
        }}
      >
        <button
          onClick={() => setThemeId(otherThemeId)}
          style={{
            width: '100%',
            background: 'var(--th-surface2)',
            border: '1px solid var(--th-border)',
            borderRadius: '3px',
            color: 'var(--th-muted)',
            fontFamily: 'var(--font-display)',
            fontSize: '0.7rem',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            padding: '0.45rem',
            cursor: 'pointer',
            transition: 'all 0.15s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem',
          }}
          onMouseEnter={e => {
            e.target.style.color = 'var(--th-text)'
            e.target.style.borderColor = 'var(--th-accent)'
          }}
          onMouseLeave={e => {
            e.target.style.color = 'var(--th-muted)'
            e.target.style.borderColor = 'var(--th-border)'
          }}
        >
          <span>{otherTheme.icon}</span>
          <span>Váltás: {otherTheme.label}</span>
        </button>
      </div>
    </aside>
  )
}
