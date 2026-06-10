import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { useSaved } from '../context/SavedResultsContext'
import RuneDivider from '../components/ui/RuneDivider'
import { useCountUp } from '../hooks/useCountUp'
import { formatRelativeTime } from '../utils/time'

function StatPill({ label, value, delay }) {
  const count = useCountUp(value)
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.45rem',
        border: '1px solid var(--th-border)',
        borderRadius: '999px',
        padding: '0.4rem 1.1rem',
        fontFamily: 'var(--font-display)',
        fontSize: '0.7rem',
        letterSpacing: '0.1em',
        color: 'var(--th-muted)',
        animation: `arch-pulse-border 3.5s ease-in-out ${delay}s infinite`,
      }}
    >
      <span style={{ color: 'var(--th-gold-lt)', fontSize: '0.95rem', fontWeight: 700 }}>
        {count}
      </span>
      {label}
    </div>
  )
}

const ACCENTS = {
  gold: { color: 'var(--th-gold)', colorLt: 'var(--th-gold-lt)', glow: 'var(--th-gold-glow)' },
  red:  { color: 'var(--th-accent-lt)', colorLt: 'var(--th-accent-lt)', glow: 'var(--th-accent-glow)' },
}

function PortalCard({ icon, title, desc, to, accent, floatDelay, fadeDelay }) {
  const navigate = useNavigate()
  const { color, colorLt, glow } = ACCENTS[accent]

  return (
    <button
      onClick={() => navigate(to)}
      style={{
        border: '1px solid var(--th-border)',
        borderRadius: '8px',
        padding: '1.4rem 1.25rem',
        textAlign: 'center',
        background: `radial-gradient(circle at 50% -10%, ${glow}, transparent 65%)`,
        cursor: 'pointer',
        color: 'inherit',
        transition: 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.35s, box-shadow 0.35s',
        animation: `fadeIn 0.25s ease ${fadeDelay}s both`,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-5px)'
        e.currentTarget.style.borderColor = color
        e.currentTarget.style.boxShadow = `0 10px 28px rgba(0,0,0,0.55), 0 0 18px ${glow}`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.borderColor = 'var(--th-border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div
        style={{
          width: '46px',
          height: '46px',
          borderRadius: '50%',
          border: `1px solid ${color}`,
          color,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 0.7rem',
          fontSize: '1.3rem',
          animation: `arch-float 4.5s ease-in-out ${floatDelay}s infinite`,
        }}
      >
        {icon}
      </div>
      <h3
        style={{
          fontFamily: 'var(--font-display)',
          letterSpacing: '0.12em',
          fontSize: '0.8rem',
          textTransform: 'uppercase',
          margin: '0 0 0.35rem',
          color: colorLt,
        }}
      >
        {title}
      </h3>
      <p
        style={{
          fontSize: '0.78rem',
          color: 'var(--th-faint)',
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

function TimelineItem({ item, isFirst, index }) {
  const navigate = useNavigate()
  const isLocation = item.type === 'location'
  const title = isLocation ? item.data.name : (item.data.character?.name ?? 'NPC')
  const sub = isLocation
    ? (item.data.location_data?.tipus ?? 'Generált helyszín')
    : `${item.data.stat_block?.race ?? ''} ${item.data.stat_block?.class ?? ''} ${item.data.stat_block?.level ?? ''}. szint`

  return (
    <div
      onClick={() => navigate('/saved')}
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: '0.7rem',
        padding: '0.5rem 0 0.5rem 0.9rem',
        borderRadius: '4px',
        cursor: 'pointer',
        transition: 'background 0.2s',
        animation: `arch-dirty-in 0.4s ease ${index * 0.08}s both`,
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'var(--th-surface2)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
    >
      <span
        style={{
          position: 'absolute',
          left: '-1.4rem',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '9px',
          height: '9px',
          borderRadius: '50%',
          background: 'var(--th-bg)',
          border: '2px solid var(--th-gold)',
          ...(isFirst
            ? { animation: 'arch-pulse-dot 2s ease-in-out infinite', boxShadow: '0 0 6px var(--th-gold-glow)' }
            : {}),
        }}
      />
      <span style={{ fontSize: '0.95rem', color: 'var(--th-gold)', width: '1.2rem', textAlign: 'center' }}>
        {isLocation ? '⌖' : '†'}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.8rem',
            letterSpacing: '0.05em',
            color: 'var(--th-text)',
            textTransform: 'uppercase',
            fontWeight: 600,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--th-faint)', fontStyle: 'italic', fontFamily: 'var(--font-lore)' }}>
          {sub}
        </div>
      </div>
      <span style={{ fontSize: '0.65rem', color: 'var(--th-faint)', fontFamily: 'var(--font-display)', whiteSpace: 'nowrap' }}>
        {formatRelativeTime(item.savedAt)}
      </span>
    </div>
  )
}

export default function Dashboard() {
  const { themeId, theme } = useTheme()
  const { saved } = useSaved()
  const recentSaved = saved.slice(0, 4)

  const stats = [
    { label: 'Mentett',  value: saved.length },
    { label: 'Helyszín', value: saved.filter(s => s.type === 'location').length },
    { label: 'NPC',      value: saved.filter(s => s.type === 'npc').length },
  ]

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '2rem' }}>
      <div style={{ maxWidth: '720px', margin: '0 auto' }}>

        {/* Hero */}
        <div style={{ textAlign: 'center', padding: '0.5rem 0 1.5rem' }}>
          <div
            style={{
              width: '68px',
              height: '68px',
              margin: '0 auto 0.85rem',
              borderRadius: '50%',
              border: '2px solid var(--th-gold)',
              borderTopColor: 'transparent',
              borderBottomColor: 'transparent',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'arch-seal-rotate 7s linear infinite',
              boxShadow: '0 0 18px var(--th-gold-glow)',
            }}
          >
            <span
              style={{
                fontSize: '1.5rem',
                color: 'var(--th-gold)',
                display: 'inline-block',
                animation: 'arch-seal-rotate 7s linear infinite reverse',
              }}
            >
              {theme.icon}
            </span>
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.6rem',
              fontWeight: 700,
              letterSpacing: '0.22em',
              color: 'var(--th-gold)',
              margin: 0,
              textShadow: '0 0 24px var(--th-gold-glow)',
            }}
          >
            {themeId === 'magus' ? 'MAGUS Archívum' : 'Star Wars Archívum'}
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-lore)',
              fontStyle: 'italic',
              color: 'var(--th-faint)',
              fontSize: '0.86rem',
              margin: '0.5rem 0 1.25rem',
              lineHeight: 1.6,
            }}
          >
            {themeId === 'magus'
              ? 'A sötétség leszáll Erionra. A Mester mindent lát — rejtett folyosókat, NPC-k titkait.'
              : 'A galaxis tele van titokkal. Az IM mindent tud — bolygók mélyén rejtőző szövetségeket.'}
          </p>
          <div style={{ display: 'flex', gap: '0.7rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {stats.map((stat, i) => (
              <StatPill key={stat.label} label={stat.label} value={stat.value} delay={i * 0.4} />
            ))}
          </div>
        </div>

        {/* Portal cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '0.5rem' }}>
          <PortalCard
            icon="⌖"
            title="Helyszín generálás"
            desc="Generálj le egy helyszínt NPC-kkel és légkörrel"
            to="/location"
            accent="gold"
            floatDelay={0}
            fadeDelay={0}
          />
          <PortalCard
            icon="†"
            title="NPC generálás"
            desc="Alkoss meg egy részletes MAGUS-karaktert"
            to="/npc"
            accent="red"
            floatDelay={0.3}
            fadeDelay={0.1}
          />
        </div>

        <RuneDivider symbol="⬥" />

        {/* Recent saves */}
        {recentSaved.length > 0 ? (
          <div>
            <p
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                letterSpacing: '0.22em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
                margin: '0 0 0.9rem',
              }}
            >
              Legutóbbi mentések
            </p>
            <div style={{ position: 'relative', paddingLeft: '1.4rem' }}>
              <div
                style={{
                  position: 'absolute',
                  left: '5px',
                  top: '6px',
                  bottom: '6px',
                  width: '1px',
                  background: 'linear-gradient(to bottom, var(--th-gold), var(--th-border))',
                }}
              />
              {recentSaved.map((item, i) => (
                <TimelineItem key={item.id} item={item} isFirst={i === 0} index={i} />
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
