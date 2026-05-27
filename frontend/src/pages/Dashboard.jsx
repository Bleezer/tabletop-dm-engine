import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { useSaved } from '../context/SavedResultsContext'
import Button from '../components/ui/Button'
import RuneDivider from '../components/ui/RuneDivider'

const MAGUS_LORE = `
  A sötétség leszáll Erionra. A mesélő szemei mindent látnak — a rejtett folyosókat,
  az NPC-k titkait, a jelenet mögött húzódó feszültséget. A Mester eszköze készen áll.
`.trim()

const SW_LORE = `
  A galaxis tele van titokkal. Az IM mindent tud — a bolygók mélyén rejtőző szövetségeket,
  az NPC-k motivációit, a Sötét Oldal árnyékát. Az Irányító Mester kész a játékra.
`.trim()

function QuickAction({ icon, title, desc, to }) {
  const navigate = useNavigate()
  return (
    <button
      onClick={() => navigate(to)}
      style={{
        background: 'var(--th-surface)',
        border: '1px solid var(--th-border)',
        borderRadius: '4px',
        padding: '1.5rem',
        cursor: 'pointer',
        textAlign: 'left',
        transition: 'all 0.2s',
        color: 'inherit',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--th-accent)'
        e.currentTarget.style.boxShadow = '0 0 16px var(--th-accent-glow)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--th-border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>{icon}</div>
      <h3
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.85rem',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'var(--th-gold)',
          margin: '0 0 0.4rem',
        }}
      >
        {title}
      </h3>
      <p style={{ fontSize: '0.9rem', color: 'var(--th-muted)', margin: 0, fontStyle: 'italic' }}>
        {desc}
      </p>
    </button>
  )
}

function RecentCard({ item }) {
  const navigate = useNavigate()
  const isLocation = item.type === 'location'
  const title = isLocation ? item.data.name : item.data.character?.name ?? 'NPC'
  const sub   = isLocation
    ? item.data.location_data?.tipus ?? 'Generált helyszín'
    : `${item.data.stat_block?.race ?? ''} ${item.data.stat_block?.class ?? ''} ${item.data.stat_block?.level ?? ''}. szint`

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.6rem 0.8rem',
        background: 'var(--th-surface)',
        border: '1px solid var(--th-border)',
        borderRadius: '3px',
        cursor: 'pointer',
      }}
      onClick={() => navigate('/saved')}
    >
      <span style={{ fontSize: '1.1rem' }}>{isLocation ? '🏰' : '⚔'}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.8rem',
            color: 'var(--th-text)',
            letterSpacing: '0.05em',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--th-muted)', fontStyle: 'italic' }}>{sub}</div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { themeId, theme } = useTheme()
  const { saved } = useSaved()
  const lore = themeId === 'magus' ? MAGUS_LORE : SW_LORE
  const recentSaved = saved.slice(0, 4)

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      {/* Hero */}
      <div
        style={{
          background: 'var(--th-surface)',
          borderBottom: '1px solid var(--th-border)',
          padding: '3rem 2rem 2rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Decorative background runes */}
        <div
          aria-hidden
          style={{
            position: 'absolute',
            top: '50%',
            right: '2rem',
            transform: 'translateY(-50%)',
            fontFamily: 'var(--font-display)',
            fontSize: '6rem',
            color: 'var(--th-border)',
            opacity: 0.4,
            userSelect: 'none',
            pointerEvents: 'none',
          }}
        >
          {theme.icon}
        </div>

        <p
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.7rem',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: 'var(--th-accent)',
            margin: '0 0 0.5rem',
          }}
        >
          DM Engine
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '2rem',
            fontWeight: 700,
            color: 'var(--th-gold)',
            margin: '0 0 1rem',
            letterSpacing: '0.08em',
          }}
        >
          {theme.label}
        </h1>
        <p
          style={{
            maxWidth: '520px',
            color: 'var(--th-muted)',
            fontSize: '0.95rem',
            fontStyle: 'italic',
            lineHeight: 1.7,
            margin: 0,
          }}
        >
          {lore}
        </p>
      </div>

      <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Stats row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
          }}
        >
          {[
            { label: 'Mentett', value: saved.length },
            { label: 'Helyszín', value: saved.filter(s => s.type === 'location').length },
            { label: 'NPC', value: saved.filter(s => s.type === 'npc').length },
          ].map(stat => (
            <div
              key={stat.label}
              style={{
                background: 'var(--th-surface)',
                border: '1px solid var(--th-border)',
                borderRadius: '3px',
                padding: '1rem',
                textAlign: 'center',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: 'var(--th-gold)',
                }}
              >
                {stat.value}
              </div>
              <div
                style={{
                  fontSize: '0.75rem',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: 'var(--th-muted)',
                  fontFamily: 'var(--font-display)',
                }}
              >
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        <RuneDivider symbol="⬥" />

        {/* Quick actions */}
        <div>
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '0.75rem',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: 'var(--th-muted)',
              margin: '0 0 0.75rem',
            }}
          >
            Gyors indítás
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <QuickAction
              icon="🏰"
              title="Helyszín generálás"
              desc="Generálj le egy helyszínt NPC-kkel és légkörrel"
              to="/location"
            />
            <QuickAction
              icon="⚔"
              title="NPC generálás"
              desc="Hozz létre egy részletes MAGUS-karaktert"
              to="/npc"
            />
          </div>
        </div>

        {/* Recent */}
        {recentSaved.length > 0 && (
          <div>
            <h2
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.75rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--th-muted)',
                margin: '0 0 0.75rem',
              }}
            >
              Legutóbbi mentések
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {recentSaved.map(item => (
                <RecentCard key={item.id} item={item} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
