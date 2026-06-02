import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { useSaved } from '../context/SavedResultsContext'
import Button from '../components/ui/Button'
import RuneDivider from '../components/ui/RuneDivider'

function QuickAction({ icon, title, desc, to }) {
  const navigate = useNavigate()
  return (
    <button
      onClick={() => navigate(to)}
      style={{
        background: 'linear-gradient(180deg, var(--th-surface2) 0%, var(--th-surface) 100%)',
        border: '1px solid var(--th-border)',
        borderRadius: '4px',
        padding: '1.25rem 1.5rem',
        cursor: 'pointer',
        textAlign: 'left',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        color: 'inherit',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--th-border-strong)'
        e.currentTarget.style.boxShadow = '0 0 0 1px var(--th-border-strong), 0 8px 24px rgba(0,0,0,0.5)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--th-border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1rem',
          color: 'var(--th-border-strong)',
          marginBottom: '0.5rem',
        }}
      >
        {icon}
      </div>
      <h3
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.78rem',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'var(--th-gold)',
          margin: '0 0 0.35rem',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          fontSize: '0.85rem',
          color: 'var(--th-muted)',
          margin: 0,
          fontFamily: 'var(--font-lore)',
          fontStyle: 'italic',
          lineHeight: 1.5,
        }}
      >
        {desc}
      </p>
    </button>
  )
}

function RecentCard({ item }) {
  const navigate = useNavigate()
  const isLocation = item.type === 'location'
  const title = isLocation ? item.data.name : (item.data.character?.name ?? 'NPC')
  const sub   = isLocation
    ? (item.data.location_data?.tipus ?? 'Generált helyszín')
    : `${item.data.stat_block?.race ?? ''} ${item.data.stat_block?.class ?? ''} ${item.data.stat_block?.level ?? ''}. szint`

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.55rem 0.85rem',
        background: 'var(--th-surface)',
        border: '1px solid var(--th-border)',
        borderRadius: '2px',
        cursor: 'pointer',
        transition: 'border-color 0.15s',
      }}
      onClick={() => navigate('/saved')}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--th-border-strong)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--th-border)'}
    >
      <span
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.8rem',
          color: 'var(--th-faint)',
          minWidth: '1rem',
          textAlign: 'center',
        }}
      >
        {isLocation ? '⌖' : '†'}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.78rem',
            color: 'var(--th-text)',
            letterSpacing: '0.04em',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontSize: '0.75rem',
            color: 'var(--th-faint)',
            fontStyle: 'italic',
            fontFamily: 'var(--font-lore)',
          }}
        >
          {sub}
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { themeId } = useTheme()
  const { saved } = useSaved()
  const recentSaved = saved.slice(0, 4)

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      {/* Archive header — compact, not a hero section */}
      <div
        style={{
          background: 'var(--th-surface)',
          borderBottom: '1px solid var(--th-border)',
          padding: '1.5rem 2rem',
        }}
      >
        <p
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.65rem',
            letterSpacing: '0.25em',
            textTransform: 'uppercase',
            color: 'var(--th-accent-lt)',
            margin: '0 0 0.35rem',
          }}
        >
          Mesélő Eszközök
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.4rem',
            fontWeight: 700,
            color: 'var(--th-gold)',
            margin: '0 0 0.4rem',
            letterSpacing: '0.1em',
          }}
        >
          {themeId === 'magus' ? 'MAGUS Archívum' : 'Star Wars Archívum'}
        </h1>
        <p
          style={{
            color: 'var(--th-faint)',
            fontSize: '0.88rem',
            fontFamily: 'var(--font-lore)',
            fontStyle: 'italic',
            margin: 0,
            lineHeight: 1.6,
          }}
        >
          {themeId === 'magus'
            ? 'A sötétség leszáll Erionra. A Mester mindent lát — rejtett folyosókat, NPC-k titkait.'
            : 'A galaxis tele van titokkal. Az IM mindent tud — bolygók mélyén rejtőző szövetségeket.'}
        </p>
      </div>

      <div style={{ padding: '1.75rem 2rem', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
          {[
            { label: 'Mentett',   value: saved.length },
            { label: 'Helyszín',  value: saved.filter(s => s.type === 'location').length },
            { label: 'NPC',       value: saved.filter(s => s.type === 'npc').length },
          ].map(stat => (
            <div
              key={stat.label}
              style={{
                background: 'linear-gradient(180deg, var(--th-surface2) 0%, var(--th-surface) 100%)',
                border: '1px solid var(--th-border)',
                borderTop: '2px solid var(--th-border-strong)',
                borderRadius: '3px',
                padding: '0.9rem 1rem',
                textAlign: 'center',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.75rem',
                  fontWeight: 700,
                  color: 'var(--th-gold)',
                  lineHeight: 1,
                }}
              >
                {stat.value}
              </div>
              <div
                style={{
                  fontSize: '0.65rem',
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  color: 'var(--th-faint)',
                  fontFamily: 'var(--font-display)',
                  marginTop: '0.3rem',
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
              fontSize: '0.65rem',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: 'var(--th-faint)',
              margin: '0 0 0.75rem',
            }}
          >
            Gyors indítás
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <QuickAction
              icon="⌖"
              title="Helyszín generálás"
              desc="Generálj le egy helyszínt NPC-kkel és légkörrel"
              to="/location"
            />
            <QuickAction
              icon="†"
              title="NPC generálás"
              desc="Alkoss meg egy részletes MAGUS-karaktert"
              to="/npc"
            />
          </div>
        </div>

        {/* Recent saves */}
        {recentSaved.length > 0 ? (
          <div>
            <h2
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
                margin: '0 0 0.6rem',
              }}
            >
              Legutóbbi mentések
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              {recentSaved.map(item => (
                <RecentCard key={item.id} item={item} />
              ))}
            </div>
          </div>
        ) : (
          <p
            style={{
              color: 'var(--th-faint)',
              fontSize: '0.85rem',
              fontFamily: 'var(--font-lore)',
              fontStyle: 'italic',
              textAlign: 'center',
              padding: '1.5rem 0',
            }}
          >
            Az archívum üres.
          </p>
        )}
      </div>
    </div>
  )
}
