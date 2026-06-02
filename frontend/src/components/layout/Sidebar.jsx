import { NavLink } from 'react-router-dom'
import { useTheme, THEMES } from '../../context/ThemeContext'
import { useSaved } from '../../context/SavedResultsContext'

const NAV = [
  { to: '/',         icon: '◈', label: 'Főoldal' },
  { to: '/location', icon: '⌖', label: 'Helyszín' },
  { to: '/npc',      icon: '†', label: 'NPC' },
  { to: '/saved',    icon: '≡', label: 'Mentések' },
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
        width: '230px',
        minWidth: '230px',
        background: 'var(--th-surface)',
        borderRight: '1px solid var(--th-border-strong)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        overflow: 'hidden',
      }}
    >
      {/* Brand */}
      <div
        style={{
          padding: '1.25rem 1rem 1rem',
          borderBottom: '1px solid var(--th-border)',
        }}
      >
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.1rem',
            color: 'var(--th-gold)',
            textAlign: 'center',
            letterSpacing: '0.15em',
            marginBottom: '0.3rem',
          }}
        >
          {theme.icon}
        </div>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.72rem',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'var(--th-gold)',
            textAlign: 'center',
            margin: '0 0 0.2rem',
          }}
        >
          {theme.label}
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-lore)',
            fontSize: '0.72rem',
            color: 'var(--th-faint)',
            textAlign: 'center',
            fontStyle: 'italic',
            margin: 0,
          }}
        >
          {theme.subtitle}
        </p>
        {/* thin gold rule */}
        <div
          style={{
            marginTop: '0.85rem',
            height: '1px',
            background: 'linear-gradient(to right, transparent, var(--th-border-strong), transparent)',
          }}
        />
      </div>

      {/* Navigation */}
      <nav
        style={{
          flex: 1,
          padding: '0.6rem 0.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '2px',
        }}
      >
        {NAV.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}
          >
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.85rem',
                minWidth: '1.1rem',
                textAlign: 'center',
                opacity: 0.8,
              }}
            >
              {icon}
            </span>
            <span>{label}</span>
            {label === 'Mentések' && saved.length > 0 && (
              <span
                style={{
                  marginLeft: 'auto',
                  background: 'var(--th-accent)',
                  color: 'var(--th-paper)',
                  fontSize: '0.62rem',
                  padding: '1px 6px',
                  borderRadius: '2px',
                  fontFamily: 'var(--font-display)',
                  letterSpacing: '0.05em',
                }}
              >
                {saved.length}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Decorative rune strip */}
      <div
        style={{
          padding: '0.4rem 1rem',
          textAlign: 'center',
          color: 'var(--th-border-strong)',
          fontSize: '0.85rem',
          letterSpacing: '0.35em',
          fontFamily: 'var(--font-display)',
          borderTop: '1px solid var(--th-border)',
          borderBottom: '1px solid var(--th-border)',
        }}
      >
        ᚱ ᚢ ᚾ ᛖ
      </div>

      {/* Theme switcher */}
      <div style={{ padding: '0.7rem' }}>
        <button
          onClick={() => setThemeId(otherThemeId)}
          style={{
            width: '100%',
            background: 'transparent',
            border: '1px solid var(--th-border)',
            borderRadius: '2px',
            color: 'var(--th-faint)',
            fontFamily: 'var(--font-display)',
            fontSize: '0.65rem',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            padding: '0.4rem',
            cursor: 'pointer',
            transition: 'all 0.15s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.color = 'var(--th-muted)'
            e.currentTarget.style.borderColor = 'var(--th-border-strong)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.color = 'var(--th-faint)'
            e.currentTarget.style.borderColor = 'var(--th-border)'
          }}
        >
          <span>{otherTheme.icon}</span>
          <span>Váltás: {otherTheme.label}</span>
        </button>
      </div>
    </aside>
  )
}
