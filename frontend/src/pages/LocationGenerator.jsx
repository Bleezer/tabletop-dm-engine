import { useState } from 'react'
import Header from '../components/layout/Header'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import RuneDivider from '../components/ui/RuneDivider'
import Badge, { ImportanceBadge, AttitudeBadge } from '../components/ui/Badge'
import { useSaved } from '../context/SavedResultsContext'
import { generateLocation } from '../api/magus'

const STAT_HU = {
  ero: 'Erő', allokepesseg: 'Áll', gyorsasag: 'Gyo',
  ugyesseg: 'Ügy', egeszseg: 'Egs', szepseg: 'Szp',
  intelligencia: 'Int', 'akaraterő': 'Aka', asztral: 'Asz',
}

function StatGrid({ stats }) {
  if (!stats) return null
  return (
    <div className="stat-grid" style={{ marginTop: '0.5rem' }}>
      {Object.entries(stats).map(([k, v]) => (
        <div key={k} className="stat-cell">
          <span style={{ fontSize: '0.6rem', color: 'var(--th-ink-muted)', fontFamily: 'var(--font-display)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            {STAT_HU[k] ?? k}
          </span>
          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--th-ink)' }}>{v}</span>
        </div>
      ))}
    </div>
  )
}

function NpcCard({ npc }) {
  const [showSecret, setShowSecret] = useState(false)

  if (npc.error) {
    return (
      <div style={{ padding: '0.75rem', background: 'rgba(139,26,26,0.1)', border: '1px solid var(--th-accent)', borderRadius: '3px', color: 'var(--th-muted)', fontSize: '0.85rem' }}>
        Hiba: {npc.error}
      </div>
    )
  }

  const char = npc.character ?? {}
  const sb   = npc.stat_block ?? {}
  const conc = npc.concept ?? {}
  const spec = npc.spec ?? {}
  const importance = conc.importance ?? spec.importance ?? 'minor'

  return (
    <div className="paper-card fade-in" style={{ padding: '1rem' }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <div>
          <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', letterSpacing: '0.08em', color: 'var(--th-ink)', margin: '0 0 0.15rem', textTransform: 'uppercase' }}>
            {char.name ?? 'Névtelen'}
          </h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--th-ink-muted)', margin: 0, fontStyle: 'italic' }}>
            {sb.race} {sb.class} {sb.level}. szint
          </p>
        </div>
        <ImportanceBadge importance={importance} />
      </div>

      {/* Role + gender */}
      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '0.6rem' }}>
        <Badge color="default">{conc.role ?? spec.role}</Badge>
        <Badge color="default">{char.gender}</Badge>
        <Badge color="default">{char.age_description}</Badge>
        <AttitudeBadge attitude={char.attitude_to_strangers} />
      </div>

      {/* Appearance + personality */}
      <p style={{ fontSize: '0.88rem', color: 'var(--th-ink)', margin: '0 0 0.4rem', lineHeight: 1.55 }}>
        <strong style={{ fontFamily: 'var(--font-display)', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--th-ink-muted)' }}>Megjelenés</strong><br />
        {char.appearance}
      </p>
      <p style={{ fontSize: '0.88rem', color: 'var(--th-ink)', margin: '0 0 0.4rem', lineHeight: 1.55 }}>
        <strong style={{ fontFamily: 'var(--font-display)', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--th-ink-muted)' }}>Személyiség</strong><br />
        {char.personality}
      </p>
      <p style={{ fontSize: '0.88rem', color: 'var(--th-ink)', margin: '0 0 0.4rem', lineHeight: 1.55 }}>
        <strong style={{ fontFamily: 'var(--font-display)', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--th-ink-muted)' }}>Motiváció</strong><br />
        {char.motivation}
      </p>
      <p style={{ fontSize: '0.85rem', color: 'var(--th-ink-muted)', margin: '0 0 0.6rem', fontStyle: 'italic' }}>
        "{char.speech_style}"
      </p>

      {/* Combat stats */}
      <div
        style={{
          background: 'rgba(0,0,0,0.1)',
          borderRadius: '2px',
          padding: '0.5rem 0.75rem',
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          fontSize: '0.85rem',
          fontFamily: 'var(--font-display)',
          marginBottom: '0.5rem',
        }}
      >
        {[
          ['ÉP', sb.combat?.ep],
          ['KÉ', sb.combat?.ke],
          ['TÉ', sb.combat?.te],
          ['VÉ', sb.combat?.ve],
          sb.combat?.ce ? ['CÉ', sb.combat.ce] : null,
          sb.combat?.hm ? ['HM', sb.combat.hm] : null,
        ].filter(Boolean).map(([label, val]) => (
          <span key={label} style={{ color: 'var(--th-ink)' }}>
            <span style={{ color: 'var(--th-ink-muted)', fontSize: '0.7rem' }}>{label} </span>
            {val}
          </span>
        ))}
      </div>

      <StatGrid stats={sb.stats} />

      {/* Secret */}
      {char.secret && (
        <div style={{ marginTop: '0.6rem' }}>
          <button
            onClick={() => setShowSecret(s => !s)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontFamily: 'var(--font-display)', fontSize: '0.72rem',
              textTransform: 'uppercase', letterSpacing: '0.06em',
              color: 'var(--th-accent)', padding: 0,
            }}
          >
            {showSecret ? '▲ Titok elrejtése' : '▼ Titok megjelenítése'}
          </button>
          {showSecret && (
            <p style={{ fontSize: '0.85rem', color: 'var(--th-ink)', fontStyle: 'italic', marginTop: '0.4rem', padding: '0.5rem', background: 'rgba(139,26,26,0.1)', borderRadius: '2px', borderLeft: '2px solid var(--th-accent)' }}>
              {char.secret}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

function LocationResult({ result, onSave }) {
  const desc = result.description ?? {}
  const ld   = result.location_data

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Title bar */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', letterSpacing: '0.1em', color: 'var(--th-gold)', margin: '0 0 0.2rem', textTransform: 'uppercase' }}>
            {result.name}
          </h2>
          {ld && (
            <p style={{ color: 'var(--th-muted)', fontSize: '0.9rem', fontStyle: 'italic', margin: 0 }}>
              {ld.negyed} — {ld.tipus}
            </p>
          )}
        </div>
        <Button variant="gold" size="sm" onClick={onSave}>Mentés</Button>
      </div>

      {/* Sensory description — parchment */}
      <div className="paper-card" style={{ padding: '1.25rem' }}>
        <p style={{ fontSize: '1rem', lineHeight: 1.75, color: 'var(--th-ink)', margin: 0, fontStyle: 'italic' }}>
          {desc.sensory_description}
        </p>
      </div>

      {/* Atmosphere */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-display)', letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--th-muted)' }}>Hangulat</span>
        <Badge color="accent">{desc.atmosphere}</Badge>
      </div>

      {/* Layout */}
      {desc.layout?.length > 0 && (
        <div style={{ background: 'var(--th-surface)', border: '1px solid var(--th-border)', borderRadius: '3px', padding: '1rem' }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--th-muted)', margin: '0 0 0.6rem' }}>
            Területek
          </h3>
          <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {desc.layout.map((area, i) => (
              <li key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', color: 'var(--th-text)', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--th-gold)', flexShrink: 0 }}>•</span>
                {area}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Current scene */}
      <div>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--th-muted)', margin: '0 0 0.4rem' }}>
          Jelenet
        </h3>
        <p style={{ color: 'var(--th-text)', fontSize: '0.95rem', lineHeight: 1.65, margin: 0 }}>
          {desc.current_scene}
        </p>
      </div>

      {/* Notable details */}
      {desc.notable_details?.length > 0 && (
        <div>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--th-muted)', margin: '0 0 0.5rem' }}>
            Érdekességek
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {desc.notable_details.map((d, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', color: 'var(--th-text)', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--th-accent)', flexShrink: 0, fontSize: '0.7rem', marginTop: '0.25rem' }}>→</span>
                {d}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* DM Notes */}
      {desc.dm_notes && (
        <div className="dm-notes-block" style={{ padding: '0.75rem 1rem', borderRadius: '2px' }}>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: '0.7rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--th-accent)', margin: '0 0 0.35rem' }}>
            Mesélőnek
          </p>
          <p style={{ color: 'var(--th-text)', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>
            {desc.dm_notes}
          </p>
        </div>
      )}

      {/* NPCs */}
      {result.npcs?.length > 0 && (
        <>
          <RuneDivider symbol="⚔" />
          <div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--th-muted)', margin: '0 0 0.75rem' }}>
              NPC-K ({result.npcs.length} db)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {result.npcs.map((npc, i) => (
                <NpcCard key={i} npc={npc} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default function LocationGenerator() {
  const [locationName, setLocationName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const { saveLocation } = useSaved()

  async function handleGenerate() {
    if (!locationName.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await generateLocation(locationName.trim())
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleGenerate()
  }

  function handleSave() {
    if (result) saveLocation(result)
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <Header
        title="Helyszín generálás"
        subtitle="Add meg a helyszín nevét — az AI lelegenerálja a leírást és az NPC-ket"
      />

      <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
        {/* Input section */}
        <div
          style={{
            background: 'var(--th-surface)',
            border: '1px solid var(--th-border)',
            borderRadius: '4px',
            padding: '1.25rem',
            marginBottom: '1.5rem',
          }}
        >
          <label
            style={{
              display: 'block',
              fontFamily: 'var(--font-display)',
              fontSize: '0.75rem',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: 'var(--th-muted)',
              marginBottom: '0.6rem',
            }}
          >
            Helyszín neve
          </label>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <input
              className="th-input"
              type="text"
              value={locationName}
              onChange={e => setLocationName(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder='pl. „Torozon Tavernája" vagy „Fekete Kapu"'
              disabled={loading}
            />
            <Button
              variant="primary"
              onClick={handleGenerate}
              disabled={loading || !locationName.trim()}
              style={{ flexShrink: 0 }}
            >
              Generálás
            </Button>
          </div>
        </div>

        {/* Loading */}
        {loading && <Spinner label="Helyszín generálása..." size={36} />}

        {/* Error */}
        {error && (
          <div
            style={{
              background: 'rgba(139,26,26,0.15)',
              border: '1px solid var(--th-accent)',
              borderRadius: '3px',
              padding: '1rem',
              color: 'var(--th-text)',
              fontSize: '0.9rem',
            }}
          >
            <strong style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Hiba:</strong>{' '}
            {error}
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <LocationResult result={result} onSave={handleSave} />
        )}
      </div>
    </div>
  )
}
