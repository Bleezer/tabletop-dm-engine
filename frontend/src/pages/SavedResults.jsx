import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/layout/Header'
import Button from '../components/ui/Button'
import Badge, { ImportanceBadge, AttitudeBadge } from '../components/ui/Badge'
import RuneDivider from '../components/ui/RuneDivider'
import { useSaved } from '../context/SavedResultsContext'
import { listKarakterek, deleteKarakter } from '../api/magus'

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('hu-HU', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return '?'
  }
}

function LocationSummary({ data }) {
  const [expanded, setExpanded] = useState(false)
  const desc = data.description ?? {}
  const ld   = data.location_data

  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.4rem' }}>
        <Badge color="accent">Helyszín</Badge>
        {ld && <Badge color="default">{ld.tipus}</Badge>}
        {ld && <Badge color="default">{ld.negyed}</Badge>}
      </div>
      <p style={{ color: 'var(--th-muted)', fontSize: '0.88rem', fontStyle: 'italic', margin: '0 0 0.5rem', lineHeight: 1.5 }}>
        {desc.sensory_description?.slice(0, 150)}{desc.sensory_description?.length > 150 ? '…' : ''}
      </p>
      {expanded && (
        <div style={{ marginTop: '0.5rem' }}>
          {desc.atmosphere && <p style={{ color: 'var(--th-text)', fontSize: '0.9rem', margin: '0 0 0.4rem' }}>Hangulat: {desc.atmosphere}</p>}
          {desc.current_scene && <p style={{ color: 'var(--th-text)', fontSize: '0.9rem', margin: '0 0 0.4rem' }}>Jelenet: {desc.current_scene}</p>}
          {data.npcs?.length > 0 && (
            <p style={{ color: 'var(--th-muted)', fontSize: '0.85rem', margin: '0 0 0.4rem', fontStyle: 'italic' }}>
              NPC-k: {data.npcs.map(n => n.character?.name ?? '?').join(', ')}
            </p>
          )}
          {desc.dm_notes && (
            <div style={{ borderLeft: '2px solid var(--th-accent)', paddingLeft: '0.6rem', marginTop: '0.4rem' }}>
              <p style={{ color: 'var(--th-muted)', fontSize: '0.85rem', fontStyle: 'italic', margin: 0 }}>{desc.dm_notes}</p>
            </div>
          )}
        </div>
      )}
      <button
        onClick={() => setExpanded(s => !s)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--th-muted)', fontSize: '0.75rem', fontFamily: 'var(--font-display)', letterSpacing: '0.06em', textTransform: 'uppercase', padding: '0.2rem 0', marginTop: '0.2rem' }}
      >
        {expanded ? '▲ Kevesebb' : '▼ Részletek'}
      </button>
    </div>
  )
}

function NpcSummary({ data }) {
  const [expanded, setExpanded] = useState(false)
  const char = data.character ?? {}
  const sb   = data.stat_block ?? {}
  const conc = data.concept ?? {}

  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.3rem' }}>
        <Badge color="gold">NPC</Badge>
        <Badge color="default">{sb.race}</Badge>
        <Badge color="default">{sb.class} {sb.level}. szint</Badge>
        <ImportanceBadge importance={conc.importance ?? 'minor'} />
      </div>
      <p style={{ color: 'var(--th-muted)', fontSize: '0.88rem', fontStyle: 'italic', margin: '0 0 0.4rem', lineHeight: 1.5 }}>
        {char.appearance?.slice(0, 120)}{char.appearance?.length > 120 ? '…' : ''}
      </p>
      {expanded && (
        <div style={{ marginTop: '0.4rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
          {char.personality && <p style={{ color: 'var(--th-text)', fontSize: '0.88rem', margin: 0 }}>Személyiség: {char.personality}</p>}
          {char.motivation && <p style={{ color: 'var(--th-text)', fontSize: '0.88rem', margin: 0 }}>Motiváció: {char.motivation}</p>}
          <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--th-muted)', fontFamily: 'var(--font-display)' }}>
            <span>ÉP {sb.combat?.ep}</span>
            <span>KÉ {sb.combat?.ke}</span>
            <span>TÉ {sb.combat?.te}</span>
            <span>VÉ {sb.combat?.ve}</span>
          </div>
          {char.attitude_to_strangers && <AttitudeBadge attitude={char.attitude_to_strangers} />}
        </div>
      )}
      <button
        onClick={() => setExpanded(s => !s)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--th-muted)', fontSize: '0.75rem', fontFamily: 'var(--font-display)', letterSpacing: '0.06em', textTransform: 'uppercase', padding: '0.2rem 0', marginTop: '0.2rem' }}
      >
        {expanded ? '▲ Kevesebb' : '▼ Részletek'}
      </button>
    </div>
  )
}

function SavedItem({ item, onRemove }) {
  const navigate   = useNavigate()
  const isLocation = item.type === 'location'
  const title = isLocation
    ? item.data.name
    : item.data.character?.name ?? 'Névtelen NPC'

  return (
    <div
      style={{
        background: 'var(--th-surface)',
        border: '1px solid var(--th-border)',
        borderRadius: '3px',
        padding: '1rem 1.1rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.1rem' }}>{isLocation ? '🏰' : '⚔'}</span>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.9rem', letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--th-gold)', margin: 0 }}>
            {title}
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {!isLocation && item.dbId && (
            <button
              onClick={() => navigate(`/karakterek/${item.dbId}`)}
              style={{
                background: 'none', border: '1px solid var(--th-border)', cursor: 'pointer',
                color: 'var(--th-muted)', fontSize: '0.68rem', padding: '1px 6px',
                fontFamily: 'var(--font-display)', letterSpacing: '0.06em', textTransform: 'uppercase',
              }}
              title="Karakterlap megnyitása"
            >
              📄 Lap
            </button>
          )}
          <span style={{ fontSize: '0.72rem', color: 'var(--th-muted)', fontStyle: 'italic' }}>{formatDate(item.savedAt)}</span>
          <button
            onClick={() => onRemove(item)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--th-muted)', fontSize: '0.75rem', padding: '0 0.2rem' }}
            title="Törlés"
          >
            ✕
          </button>
        </div>
      </div>

      {isLocation
        ? <LocationSummary data={item.data} />
        : <NpcSummary data={item.data} />
      }
    </div>
  )
}

const FILTERS = [
  { id: 'all',      label: 'Összes' },
  { id: 'location', label: 'Helyszínek' },
  { id: 'npc',      label: 'NPC-k' },
]

function npcRowToItem(k) {
  return {
    type: 'npc',
    id: `db-${k.id}`,
    dbId: k.id,
    savedAt: k.letrehozva,
    data: {
      character: k.character,
      stat_block: k.stat_block,
      concept: k.concept,
    },
  }
}

export default function SavedResults() {
  const { saved, remove, clearAll } = useSaved()
  const [apiNpcs, setApiNpcs] = useState([])
  const [filter, setFilter] = useState('all')
  const [confirmClear, setConfirmClear] = useState(false)

  useEffect(() => {
    listKarakterek()
      .then(rows => setApiNpcs(rows.map(npcRowToItem)))
      .catch(() => {})
  }, [])

  // Merge: API NPCs first (newest), then localStorage locations
  const allItems = [
    ...apiNpcs,
    ...saved.filter(s => s.type === 'location'),
  ]
  const filtered = filter === 'all' ? allItems : allItems.filter(s => s.type === filter)
  const totalCount = allItems.length

  async function handleRemove(item) {
    if (item.dbId) {
      try {
        await deleteKarakter(item.dbId)
        setApiNpcs(prev => prev.filter(n => n.dbId !== item.dbId))
      } catch {
        // ignore
      }
    } else {
      remove(item.id)
    }
  }

  function handleClear() {
    if (confirmClear) {
      clearAll()
      setConfirmClear(false)
    } else {
      setConfirmClear(true)
    }
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <Header
        title="Mentett eredmények"
        subtitle={`${totalCount} mentett helyszín és NPC`}
      />

      <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
        {/* Filter + clear row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '0.4rem' }}>
            {FILTERS.map(f => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                style={{
                  background: filter === f.id ? 'var(--th-accent)' : 'var(--th-surface)',
                  border: `1px solid ${filter === f.id ? 'var(--th-accent)' : 'var(--th-border)'}`,
                  borderRadius: '3px',
                  color: filter === f.id ? '#fff' : 'var(--th-muted)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.72rem',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  padding: '0.35rem 0.75rem',
                  cursor: 'pointer',
                }}
              >
                {f.label}
                {f.id !== 'all' && (
                  <span style={{ marginLeft: '0.3rem', opacity: 0.7 }}>
                    ({allItems.filter(s => s.type === f.id).length})
                  </span>
                )}
              </button>
            ))}
          </div>

          {saved.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              style={{ color: confirmClear ? 'var(--th-accent-lt)' : undefined }}
            >
              {confirmClear ? 'Biztosan törlöd?' : 'Helyszínek törlése'}
            </Button>
          )}
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              padding: '4rem 2rem',
              color: 'var(--th-muted)',
              fontStyle: 'italic',
            }}
          >
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📜</div>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: '0.85rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--th-border)' }}>
              {totalCount === 0 ? 'Még nincs mentett elem' : 'Nincs ilyen típusú mentés'}
            </p>
          </div>
        )}

        {/* List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filtered.map(item => (
            <SavedItem key={item.id} item={item} onRemove={handleRemove} />
          ))}
        </div>
      </div>
    </div>
  )
}
