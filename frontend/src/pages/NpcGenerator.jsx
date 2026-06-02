import { useState } from 'react'
import Header from '../components/layout/Header'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import Badge, { ImportanceBadge, AttitudeBadge } from '../components/ui/Badge'
import RuneDivider from '../components/ui/RuneDivider'
import { generateNpc } from '../api/magus'

const STAT_HU = {
  ero: 'Erő', allokepesseg: 'Áll', gyorsasag: 'Gyo',
  ugyesseg: 'Ügy', egeszseg: 'Egs', szepseg: 'Szp',
  intelligencia: 'Int', 'akaraterő': 'Aka', asztral: 'Asz',
}

function DossierField({ label, children }) {
  if (!children) return null
  return (
    <div style={{ marginBottom: '0.7rem' }}>
      <p
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.62rem',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'var(--th-faint)',
          margin: '0 0 0.2rem',
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontSize: '0.9rem',
          color: 'var(--th-ink)',
          fontFamily: 'var(--font-lore)',
          lineHeight: 1.6,
          margin: 0,
        }}
      >
        {children}
      </p>
    </div>
  )
}

function StatRow({ label, value }) {
  if (value == null) return null
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0.2rem 0',
        borderBottom: '1px solid rgba(0,0,0,0.1)',
      }}
    >
      <span
        style={{
          fontSize: '0.68rem',
          color: 'var(--th-ink-muted)',
          fontFamily: 'var(--font-display)',
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
        }}
      >
        {label}
      </span>
      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--th-ink)' }}>{value}</span>
    </div>
  )
}

function NpcResult({ npc }) {
  const [showSecret, setShowSecret] = useState(false)

  const char = npc.character ?? {}
  const sb   = npc.stat_block ?? {}
  const conc = npc.concept ?? {}
  const importance = conc.importance ?? 'minor'

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Dossier header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          paddingBottom: '0.75rem',
          borderBottom: '1px solid var(--th-border-strong)',
        }}
      >
        <div>
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.4rem',
              letterSpacing: '0.12em',
              color: 'var(--th-gold)',
              margin: '0 0 0.2rem',
              textTransform: 'uppercase',
            }}
          >
            {char.name ?? 'Névtelen'}
          </h2>
          <p style={{ color: 'var(--th-muted)', fontSize: '0.88rem', fontStyle: 'italic', margin: 0 }}>
            {sb.race} {sb.class} — {sb.level}. szint
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <ImportanceBadge importance={importance} />
          {npc.id && (
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.62rem',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
              }}
            >
              ✓ #{npc.id}
            </span>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        {/* Left: character dossier */}
        <div
          className="paper-card"
          style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column' }}
        >
          {/* Badges */}
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <Badge color="default">{char.gender}</Badge>
            <Badge color="default">{char.age_description}</Badge>
            <AttitudeBadge attitude={char.attitude_to_strangers} />
          </div>

          <DossierField label="Megjelenés">{char.appearance}</DossierField>
          <DossierField label="Személyiség">{char.personality}</DossierField>
          <DossierField label="Háttér">{char.background}</DossierField>
          <DossierField label="Motiváció">{char.motivation}</DossierField>

          {char.speech_style && (
            <p
              style={{
                fontSize: '0.88rem',
                color: 'var(--th-ink-muted)',
                fontFamily: 'var(--font-lore)',
                fontStyle: 'italic',
                margin: '0 0 0.75rem',
                paddingLeft: '0.75rem',
                borderLeft: '2px solid var(--th-paper-dk)',
              }}
            >
              „{char.speech_style}"
            </p>
          )}

          {/* Secret panel */}
          {char.secret && (
            <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
              <button
                onClick={() => setShowSecret(s => !s)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.65rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  color: 'var(--th-accent-lt)',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                }}
              >
                <span>{showSecret ? '▲' : '▼'}</span>
                <span>Mesélői titok</span>
              </button>
              {showSecret && (
                <div className="secret-block" style={{ marginTop: '0.4rem' }}>
                  <p
                    style={{
                      fontSize: '0.88rem',
                      color: 'var(--th-ink)',
                      fontFamily: 'var(--font-lore)',
                      fontStyle: 'italic',
                      margin: 0,
                      lineHeight: 1.55,
                    }}
                  >
                    {char.secret}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Combat values */}
          <div
            style={{
              background: 'linear-gradient(180deg, var(--th-surface2), var(--th-surface))',
              border: '1px solid var(--th-border)',
              borderTop: '2px solid var(--th-border-strong)',
              borderRadius: '3px',
              padding: '0.9rem 1rem',
            }}
          >
            <p
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
                margin: '0 0 0.7rem',
              }}
            >
              Harci értékek
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.4rem' }}>
              {[
                ['ÉP', sb.combat?.ep],
                ['KÉ', sb.combat?.ke],
                ['TÉ', sb.combat?.te],
                ['VÉ', sb.combat?.ve],
                ['CÉ', sb.combat?.ce],
                ['HM', sb.combat?.hm],
              ]
                .filter(([, v]) => v != null)
                .map(([label, val]) => (
                  <div
                    key={label}
                    style={{
                      textAlign: 'center',
                      padding: '0.4rem 0.2rem',
                      background: 'rgba(0,0,0,0.2)',
                      borderRadius: '2px',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.6rem',
                        fontFamily: 'var(--font-display)',
                        letterSpacing: '0.08em',
                        color: 'var(--th-faint)',
                        textTransform: 'uppercase',
                      }}
                    >
                      {label}
                    </div>
                    <div
                      style={{
                        fontSize: '1.05rem',
                        fontWeight: 700,
                        color: 'var(--th-gold)',
                        lineHeight: 1.2,
                      }}
                    >
                      {val}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Attributes */}
          {sb.stats && (
            <div
              style={{
                background: 'linear-gradient(180deg, var(--th-surface2), var(--th-surface))',
                border: '1px solid var(--th-border)',
                borderRadius: '3px',
                padding: '0.9rem 1rem',
              }}
            >
              <p
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.65rem',
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  color: 'var(--th-faint)',
                  margin: '0 0 0.6rem',
                }}
              >
                Tulajdonságok
              </p>
              {Object.entries(sb.stats).map(([k, v]) => (
                <StatRow key={k} label={STAT_HU[k] ?? k} value={v} />
              ))}
            </div>
          )}

          {/* Meta */}
          <div
            style={{
              background: 'var(--th-surface)',
              border: '1px solid var(--th-border)',
              borderRadius: '3px',
              padding: '0.75rem 1rem',
            }}
          >
            <StatRow label="Összpont" value={sb.total_points} />
            <StatRow label="Szerep" value={conc.role} />
          </div>
        </div>
      </div>
    </div>
  )
}

const EXAMPLE_ROLES = [
  'fogadós — kövér, vidám ember',
  'őr — gyanakvó, komoly katona',
  'tolvaj — ideges, fiatal srác',
  'kereskedő — ravasz, középkorú nő',
]

export default function NpcGenerator() {
  const [locationCtx, setLocationCtx] = useState('')
  const [roleHint, setRoleHint]       = useState('')
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)
  const [result, setResult]           = useState(null)

  async function handleGenerate() {
    if (!roleHint.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await generateNpc(locationCtx.trim(), roleHint.trim())
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <Header
        title="NPC Generálás"
        subtitle="Önálló karakter létrehozása — faj, kaszt és szint automatikus meghatározással"
      />

      <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
        {/* Input panel */}
        <div
          style={{
            background: 'linear-gradient(180deg, var(--th-surface2) 0%, var(--th-surface) 100%)',
            border: '1px solid var(--th-border)',
            borderRadius: '4px',
            padding: '1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <div>
            <label
              style={{
                display: 'block',
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
                marginBottom: '0.5rem',
              }}
            >
              Szerep / rövid leírás
            </label>
            <input
              className="th-input"
              type="text"
              value={roleHint}
              onChange={e => setRoleHint(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleGenerate()}
              placeholder='pl. „fogadós — kövér, barátságos" vagy „rejtélyes varázsló"'
              disabled={loading}
            />
            <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.45rem', flexWrap: 'wrap' }}>
              {EXAMPLE_ROLES.map(r => (
                <button
                  key={r}
                  onClick={() => setRoleHint(r)}
                  style={{
                    background: 'var(--th-surface)',
                    border: '1px solid var(--th-border)',
                    borderRadius: '2px',
                    color: 'var(--th-faint)',
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-lore)',
                    fontStyle: 'italic',
                    transition: 'border-color 0.1s, color 0.1s',
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
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label
              style={{
                display: 'block',
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--th-faint)',
                marginBottom: '0.5rem',
              }}
            >
              Helyszín kontextus{' '}
              <span style={{ fontWeight: 400, textTransform: 'none', fontSize: '0.6rem', color: 'var(--th-faint)' }}>
                (opcionális)
              </span>
            </label>
            <textarea
              className="th-input"
              rows={3}
              value={locationCtx}
              onChange={e => setLocationCtx(e.target.value)}
              placeholder="A helyszín rövid leírása: jelleg, hangulat, frakció..."
              disabled={loading}
              style={{ resize: 'vertical' }}
            />
          </div>

          <Button
            variant="primary"
            onClick={handleGenerate}
            disabled={loading || !roleHint.trim()}
          >
            NPC generálása
          </Button>
        </div>

        {loading && <Spinner label="NPC generálása..." size={36} />}

        {error && (
          <div
            style={{
              background: 'rgba(122, 30, 30, 0.15)',
              border: '1px solid var(--th-accent)',
              borderRadius: '3px',
              padding: '0.85rem 1rem',
              color: 'var(--th-danger)',
              fontSize: '0.88rem',
            }}
          >
            <strong
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.65rem',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                display: 'block',
                marginBottom: '0.2rem',
              }}
            >
              Hiba
            </strong>
            {error}
          </div>
        )}

        {result && !loading && <NpcResult npc={result} />}
      </div>
    </div>
  )
}
