import { useState, useEffect, useRef } from 'react'
import Header from '../components/layout/Header'
import Spinner from '../components/ui/Spinner'
import {
  listArchetipusok, getArchetipus, createArchetipus,
  updateArchetipus, deleteArchetipus, listKepzettsegek,
} from '../api/magus'

// ── constants ────────────────────────────────────────────────────────────────

const ICONS = ['⚔', '🗡️', '🛡️', '☩', '✦', '☿', '♆', '🔥', '👁️', '⚗️', '🌙', '♜']

const CARD_COLORS = [
  '#c9a040','#8a1e1e','#2a5a7a','#3a6a1e',
  '#5a1e7a','#7a5a1e','#1e5a5a','#7a3a1e',
]

const KATEGORIA_LABEL = {
  harci: 'Harci', tudomanyos: 'Tudományos', vilagi: 'Világi', alvilagi: 'Alvilági',
}

function emptyEditor() {
  return { nev: '', leiras: '', ikon: '⚔', kepzettsegek: [] }
}

// pick a deterministic accent color from the card's index or id
function accentFor(idx) {
  return CARD_COLORS[idx % CARD_COLORS.length]
}

// ── sub-components ────────────────────────────────────────────────────────────

function ArchCard({ arch, index, isSelected, onClick }) {
  const [hovered, setHovered] = useState(false)
  const accent = accentFor(index)
  const active = isSelected || hovered

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 108,
        flexShrink: 0,
        background: 'linear-gradient(160deg,#1a1208 0%,#0e0904 60%,#0c0803 100%)',
        border: `1px solid ${isSelected ? 'var(--th-gold)' : active ? '#5a3a10' : '#2a1a04'}`,
        cursor: 'pointer',
        position: 'relative',
        transition: 'transform 0.25s cubic-bezier(.34,1.56,.64,1), box-shadow 0.25s, border-color 0.2s',
        transform: isSelected ? 'translateY(-10px) scale(1.03)' : hovered ? 'translateY(-8px) scale(1.02)' : 'none',
        boxShadow: isSelected
          ? `0 20px 40px rgba(0,0,0,.8), 0 0 0 1px rgba(201,160,64,.3), 0 0 28px rgba(201,160,64,.15)`
          : hovered
            ? `0 16px 30px rgba(0,0,0,.7), 0 0 18px rgba(138,96,32,.18)`
            : '0 4px 12px rgba(0,0,0,.6)',
        padding: 0,
        outline: 'none',
        textAlign: 'left',
      }}
    >
      {/* top accent strip */}
      <div style={{
        height: 2,
        background: isSelected
          ? `linear-gradient(to right, ${accent}, var(--th-gold), ${accent})`
          : accent,
        boxShadow: isSelected ? `0 0 10px var(--th-gold-glow)` : 'none',
        transition: 'box-shadow 0.2s',
      }} />

      {/* corner ornaments */}
      {active && (
        <>
          <span style={{ position:'absolute', top:6, left:6, fontSize:6, color:'var(--th-gold-dk,#8a6020)', lineHeight:1 }}>◈</span>
          <span style={{ position:'absolute', top:6, right:6, fontSize:6, color:'var(--th-gold-dk,#8a6020)', lineHeight:1 }}>◈</span>
        </>
      )}

      {/* icon area */}
      <div style={{ padding:'14px 10px 8px', textAlign:'center', position:'relative' }}>
        {active && (
          <div style={{
            position:'absolute', inset:0,
            background:`radial-gradient(circle at 50% 70%, ${accent}22 0%, transparent 70%)`,
          }} />
        )}
        <span style={{
          fontSize: 28,
          lineHeight: 1,
          display: 'block',
          position: 'relative',
          transition: 'transform 0.25s cubic-bezier(.34,1.56,.64,1), filter 0.25s',
          transform: active ? 'scale(1.14)' : 'scale(1)',
          filter: isSelected
            ? 'drop-shadow(0 3px 8px rgba(0,0,0,.9)) drop-shadow(0 0 10px rgba(201,160,64,.3))'
            : 'drop-shadow(0 3px 6px rgba(0,0,0,.9))',
          animation: isSelected ? 'arch-float 4s ease-in-out infinite' : 'none',
        }}>
          {arch.ikon}
        </span>
      </div>

      {/* name + pips */}
      <div style={{
        padding:'6px 8px 10px', textAlign:'center',
        borderTop:'1px solid rgba(42,26,4,.8)',
      }}>
        <div style={{
          fontFamily:'var(--font-display)',
          fontSize: 7.5,
          fontWeight: 600,
          letterSpacing:'0.08em',
          textTransform:'uppercase',
          lineHeight: 1.35,
          color: isSelected ? 'var(--th-gold)' : hovered ? 'var(--th-text)' : 'var(--th-faint)',
          transition:'color 0.2s',
        }}>
          {arch.nev}
        </div>
        <div style={{ display:'flex', justifyContent:'center', gap:3, marginTop:5 }}>
          {Array.from({ length: Math.min(arch.kepzettseg_szam ?? 0, 8) }).map((_, i) => (
            <div key={i} style={{
              width:4, height:4, borderRadius:'50%',
              background: isSelected ? 'var(--th-gold-dk,#8a6020)' : '#2a1a04',
              boxShadow: isSelected ? '0 0 4px var(--th-gold-glow)' : 'none',
              transition:'background 0.2s, box-shadow 0.2s',
            }} />
          ))}
        </div>
      </div>
    </button>
  )
}

function NewCard({ onClick }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 80, height: 142, flexShrink: 0,
        background: hovered ? 'rgba(201,160,64,.04)' : 'transparent',
        border: `1px dashed ${hovered ? 'var(--th-gold-dk,#8a6020)' : '#2a1a04'}`,
        cursor: 'pointer',
        display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8,
        transition:'border-color 0.2s, background 0.2s, transform 0.2s',
        transform: hovered ? 'translateY(-4px)' : 'none',
        outline:'none',
      }}
    >
      <span style={{
        fontSize:22, lineHeight:1,
        color: hovered ? 'var(--th-gold-dk,#8a6020)' : '#2a1a04',
        transition:'color 0.2s, transform 0.2s',
        display:'block',
        transform: hovered ? 'scale(1.1) rotate(90deg)' : 'none',
      }}>+</span>
      <span style={{
        fontFamily:'var(--font-display)', fontSize:6,
        letterSpacing:'0.15em', textTransform:'uppercase',
        color: hovered ? 'var(--th-gold-dk,#8a6020)' : '#2a1a04',
        textAlign:'center', lineHeight:1.5,
        transition:'color 0.2s',
      }}>Új<br/>Archetípus</span>
    </button>
  )
}

function IconPicker({ value, onChange }) {
  return (
    <div style={{ display:'flex', flexWrap:'wrap', gap:5, marginTop:'0.3rem' }}>
      {ICONS.map(icon => (
        <button
          key={icon}
          onClick={() => onChange(icon)}
          style={{
            width:32, height:32,
            border: `1px solid ${value === icon ? 'var(--th-gold)' : '#2a1a04'}`,
            background: value === icon ? 'rgba(201,160,64,.12)' : 'rgba(0,0,0,.3)',
            display:'flex', alignItems:'center', justifyContent:'center',
            fontSize:16, cursor:'pointer',
            boxShadow: value === icon ? '0 0 8px var(--th-gold-glow), inset 0 0 4px rgba(201,160,64,.1)' : 'none',
            transition:'border-color 0.15s, background 0.15s, transform 0.15s, box-shadow 0.15s',
            outline:'none',
          }}
          onMouseEnter={e => { if (value !== icon) { e.currentTarget.style.borderColor='var(--th-gold-dk,#8a6020)'; e.currentTarget.style.transform='scale(1.15)' }}}
          onMouseLeave={e => { if (value !== icon) { e.currentTarget.style.borderColor='#2a1a04'; e.currentTarget.style.transform='scale(1)' }}}
        >
          {icon}
        </button>
      ))}
    </div>
  )
}

function SkillRow({ item, index, total, allSkills, onChange, onMoveUp, onMoveDown, onRemove }) {
  const [hovered, setHovered] = useState(false)
  const skill = allSkills.find(s => s.id === item.kepzettseg_id)
  const isMester = item.cel_fok === 'mester'
  const ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X']

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display:'grid',
        gridTemplateColumns:'32px 1fr auto auto auto',
        alignItems:'center', gap:'0.75rem',
        padding:'0.55rem 0.7rem',
        border: `1px solid ${hovered ? 'rgba(42,26,4,.8)' : 'transparent'}`,
        background: hovered ? 'rgba(201,160,64,.04)' : 'transparent',
        marginBottom:2,
        transition:'background 0.15s, border-color 0.15s',
      }}
    >
      <div style={{
        fontFamily:'var(--font-display)', fontSize:'0.68rem', fontWeight:600,
        letterSpacing:'0.05em', textAlign:'center',
        color: hovered ? 'var(--th-gold-dk,#8a6020)' : '#3a2808',
        transition:'color 0.15s',
      }}>
        {ROMAN[index] ?? index + 1}
      </div>

      <div>
        <span style={{ fontStyle:'italic', fontSize:'0.98rem', color:'var(--th-text)', display:'block', lineHeight:1 }}>
          {skill?.nev ?? '—'}
        </span>
        <span style={{ fontSize:'0.65rem', color:'var(--th-faint)', letterSpacing:'0.05em' }}>
          {KATEGORIA_LABEL[skill?.kategoria]}
        </span>
      </div>

      <button
        onClick={() => onChange({ ...item, cel_fok: skill?.tipus === 'szazalekos' ? 'szazalekos' : isMester ? 'alap' : 'mester' })}
        title="Kattints a váltáshoz"
        style={{
          fontFamily:'var(--font-display)', fontSize:'0.57rem',
          letterSpacing:'0.14em', textTransform:'uppercase',
          padding:'2px 8px', border:'1px solid',
          borderColor: isMester ? 'var(--th-gold-dk,#8a6020)' : '#3a2808',
          color: isMester ? 'var(--th-gold)' : 'var(--th-faint)',
          background: isMester ? 'rgba(201,160,64,.06)' : 'transparent',
          cursor: skill?.tipus === 'szazalekos' ? 'default' : 'pointer',
          transition:'all 0.15s', outline:'none',
        }}
      >
        {item.cel_fok === 'szazalekos' ? '%' : isMester ? 'Mester' : 'Alap'}
      </button>

      <div style={{ display:'flex', flexDirection:'column', gap:1 }}>
        {[['▲', onMoveUp, index === 0], ['▼', onMoveDown, index === total - 1]].map(([label, fn, disabled]) => (
          <button key={label} onClick={fn} disabled={disabled} style={{
            background:'transparent', border:'1px solid #2a1a04',
            color: disabled ? '#1a1006' : '#3a2808',
            fontSize:'0.5rem', padding:'1px 5px', cursor: disabled ? 'default' : 'pointer',
            lineHeight:1.3, transition:'color 0.1s, border-color 0.1s, background 0.1s',
            outline:'none',
          }}
            onMouseEnter={e => { if (!disabled) { e.currentTarget.style.color='var(--th-gold)'; e.currentTarget.style.borderColor='var(--th-gold-dk,#8a6020)'; e.currentTarget.style.background='rgba(201,160,64,.06)' }}}
            onMouseLeave={e => { if (!disabled) { e.currentTarget.style.color='#3a2808'; e.currentTarget.style.borderColor='#2a1a04'; e.currentTarget.style.background='transparent' }}}
          >{label}</button>
        ))}
      </div>

      <button onClick={onRemove} style={{
        background:'transparent', border:'1px solid transparent',
        color:'#3a2808', fontSize:'0.7rem', cursor:'pointer',
        padding:'2px 5px', borderRadius:2, transition:'color 0.15s, border-color 0.15s, background 0.15s',
        outline:'none',
      }}
        onMouseEnter={e => { e.currentTarget.style.color='#c04040'; e.currentTarget.style.borderColor='#7a1e1e'; e.currentTarget.style.background='rgba(122,30,30,.1)' }}
        onMouseLeave={e => { e.currentTarget.style.color='#3a2808'; e.currentTarget.style.borderColor='transparent'; e.currentTarget.style.background='transparent' }}
      >✕</button>
    </div>
  )
}

function AddSkillRow({ allSkills, existingIds, onAdd }) {
  const [selId, setSelId] = useState('')
  const [celFok, setCelFok] = useState('alap')
  const skill = allSkills.find(s => s.id === Number(selId))

  function handleSkillChange(e) {
    setSelId(e.target.value)
    const sk = allSkills.find(s => s.id === Number(e.target.value))
    setCelFok(sk?.tipus === 'szazalekos' ? 'szazalekos' : 'alap')
  }

  function handleAdd() {
    if (!selId) return
    onAdd({ kepzettseg_id: Number(selId), cel_fok: celFok })
    setSelId(''); setCelFok('alap')
  }

  const available = allSkills.filter(s => !existingIds.has(s.id))
  const grouped = Object.entries(
    available.reduce((acc, s) => { (acc[s.kategoria] = acc[s.kategoria] || []).push(s); return acc }, {})
  )

  const selStyle = {
    background:'rgba(0,0,0,.4)', border:'1px solid #2a1a04',
    color:'var(--th-faint)', fontFamily:'var(--font-lore)',
    fontStyle:'italic', fontSize:'0.88rem',
    padding:'0.3rem 0.5rem', outline:'none', cursor:'pointer',
    transition:'border-color 0.2s',
  }

  return (
    <div style={{
      display:'grid', gridTemplateColumns:'1fr 90px auto',
      gap:'0.5rem', padding:'0.6rem 0.7rem', marginTop:'0.4rem',
      background:'rgba(0,0,0,.2)', border:'1px dashed #2a1a04', alignItems:'center',
    }}>
      <select value={selId} onChange={handleSkillChange} style={selStyle}>
        <option value="">— Képzettség hozzáadása —</option>
        {grouped.map(([kat, skills]) => (
          <optgroup key={kat} label={KATEGORIA_LABEL[kat] ?? kat}>
            {skills.map(s => (
              <option key={s.id} value={s.id}>
                {s.nev}{s.tipus === 'szazalekos' ? ' (%)' : ''}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      <select value={celFok} onChange={e => setCelFok(e.target.value)}
        disabled={skill?.tipus === 'szazalekos'}
        style={{ ...selStyle, fontFamily:'var(--font-display)', fontStyle:'normal', fontSize:'0.65rem', letterSpacing:'0.08em' }}
      >
        {skill?.tipus === 'szazalekos'
          ? <option value="szazalekos">%</option>
          : <><option value="alap">Alap</option><option value="mester">Mester</option></>
        }
      </select>

      <button onClick={handleAdd} disabled={!selId} style={{
        fontFamily:'var(--font-display)', fontSize:'0.6rem',
        letterSpacing:'0.12em', textTransform:'uppercase',
        background:'transparent', border:'1px solid #3a2808',
        color:'var(--th-faint)', padding:'0.35rem 0.9rem',
        cursor: selId ? 'pointer' : 'default',
        opacity: selId ? 1 : 0.4,
        transition:'all 0.15s', outline:'none',
        whiteSpace:'nowrap',
      }}
        onMouseEnter={e => { if (selId) { e.currentTarget.style.borderColor='var(--th-gold-dk,#8a6020)'; e.currentTarget.style.color='var(--th-gold)'; e.currentTarget.style.background='rgba(201,160,64,.07)' }}}
        onMouseLeave={e => { e.currentTarget.style.borderColor='#3a2808'; e.currentTarget.style.color='var(--th-faint)'; e.currentTarget.style.background='transparent' }}
      >+ Felvesz</button>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ArchetypeManager() {
  const [archetypes, setArchetypes] = useState([])
  const [allSkills, setAllSkills]   = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [editor, setEditor]         = useState(emptyEditor())
  const [loading, setLoading]       = useState(true)
  const [saving, setSaving]         = useState(false)
  const [error, setError]           = useState(null)
  const [dirty, setDirty]           = useState(false)

  useEffect(() => {
    Promise.all([listArchetipusok(), listKepzettsegek()])
      .then(([archs, skills]) => { setArchetypes(archs); setAllSkills(skills) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function refreshList() {
    const archs = await listArchetipusok()
    setArchetypes(archs)
    return archs
  }

  function selectArchetype(id) {
    if (dirty && !window.confirm('Elmentetlen változások. Folytatod?')) return
    setSelectedId(id)
    setDirty(false)
    setError(null)
    if (id === null) {
      setEditor(emptyEditor())
    } else {
      setLoading(true)
      getArchetipus(id)
        .then(arch => setEditor({
          nev: arch.nev,
          leiras: arch.leiras ?? '',
          ikon: arch.ikon ?? '⚔',
          kepzettsegek: arch.kepzettsegek.map(k => ({ kepzettseg_id: k.kepzettseg_id, cel_fok: k.cel_fok })),
        }))
        .catch(e => setError(e.message))
        .finally(() => setLoading(false))
    }
  }

  function updateEditor(patch) {
    setEditor(prev => ({ ...prev, ...patch }))
    setDirty(true)
  }

  function addSkill(item)             { updateEditor({ kepzettsegek: [...editor.kepzettsegek, item] }) }
  function removeSkill(i)             { updateEditor({ kepzettsegek: editor.kepzettsegek.filter((_, j) => j !== i) }) }
  function changeSkill(i, item)       { updateEditor({ kepzettsegek: editor.kepzettsegek.map((k, j) => j === i ? item : k) }) }
  function moveSkill(i, dir) {
    const list = [...editor.kepzettsegek]
    const t = i + dir
    if (t < 0 || t >= list.length) return
    ;[list[i], list[t]] = [list[t], list[i]]
    updateEditor({ kepzettsegek: list })
  }

  async function handleSave() {
    if (!editor.nev.trim()) { setError('Az archetípus neve kötelező.'); return }
    setSaving(true); setError(null)
    try {
      const body = { nev: editor.nev.trim(), leiras: editor.leiras || null, ikon: editor.ikon, kepzettsegek: editor.kepzettsegek }
      if (selectedId === null) {
        const saved = await createArchetipus(body)
        setSelectedId(saved.id)
      } else {
        await updateArchetipus(selectedId, body)
      }
      setDirty(false)
      await refreshList()
    } catch(e) { setError(e.message) }
    finally { setSaving(false) }
  }

  async function handleDelete() {
    if (!window.confirm(`Törlöd: "${editor.nev}"?`)) return
    setSaving(true)
    try {
      await deleteArchetipus(selectedId)
      setSelectedId(null); setEditor(emptyEditor()); setDirty(false)
      await refreshList()
    } catch(e) { setError(e.message) }
    finally { setSaving(false) }
  }

  const existingIds = new Set(editor.kepzettsegek.map(k => k.kepzettseg_id))
  const selectedArch = archetypes.find(a => a.id === selectedId)
  const isNew = selectedId === null

  return (
    <div style={{ display:'flex', flexDirection:'column', minHeight:'100%' }}>

      {/* ── Page Header ── */}
      <div style={{
        padding:'1.75rem 2.5rem 1.25rem',
        position:'relative',
        background:'radial-gradient(ellipse 60% 120px at 50% -20px, rgba(201,160,64,.06) 0%, transparent 100%)',
        borderBottom:'1px solid #1e1206',
      }}>
        <div style={{
          position:'absolute', bottom:-1, left:'10%', right:'10%',
          height:1, background:'linear-gradient(to right, transparent, var(--th-gold-dk,#8a6020), transparent)',
        }} />
        <div style={{ fontFamily:'var(--font-display)', fontSize:'0.58rem', letterSpacing:'0.25em', color:'var(--th-faint)', textTransform:'uppercase', marginBottom:'0.4rem' }}>
          Magus · Mesélői Eszközök
        </div>
        <h1 style={{
          fontFamily:'var(--font-display)', fontSize:'1.8rem', fontWeight:700,
          letterSpacing:'0.12em', textTransform:'uppercase', lineHeight:1, margin:0,
          color:'var(--th-gold)',
          textShadow:'0 0 40px rgba(201,160,64,.28), 0 0 80px rgba(201,160,64,.1), 0 2px 4px rgba(0,0,0,.8)',
        }}>Archetípus Kódex</h1>
        <p style={{ fontStyle:'italic', fontSize:'0.92rem', color:'var(--th-faint)', marginTop:'0.25rem' }}>
          Kaszttól független képzettség‑prioritás tervek
        </p>
        {/* pulsing dots */}
        <div style={{ position:'absolute', top:'50%', right:'2.5rem', transform:'translateY(-50%)', display:'flex', gap:'0.4rem', alignItems:'center' }}>
          {[0, 0.5, 1].map((delay, i) => (
            <div key={i} style={{
              width: i === 1 ? 6 : 4, height: i === 1 ? 6 : 4,
              borderRadius:'50%', background:'var(--th-gold-dk,#8a6020)',
              boxShadow:'0 0 6px var(--th-gold-glow)',
              animation:`arch-pulse-dot 3s ease-in-out ${delay}s infinite`,
            }} />
          ))}
        </div>
      </div>

      {error && (
        <div style={{
          margin:'0.75rem 2.5rem 0',
          background:'rgba(122,30,30,.2)', border:'1px solid var(--th-accent)',
          color:'var(--th-danger)', padding:'0.5rem 0.75rem',
          fontSize:'0.82rem', borderRadius:2,
        }}>{error}</div>
      )}

      {loading && !archetypes.length ? (
        <div style={{ display:'flex', justifyContent:'center', paddingTop:'4rem' }}><Spinner /></div>
      ) : (
        <>
          {/* ── Card Strip ── */}
          <div style={{
            padding:'2rem 2.5rem 0',
            overflowX:'auto',
            background:'radial-gradient(ellipse 80% 200px at 50% 50%, rgba(201,160,64,.025) 0%, transparent 100%)',
            scrollbarWidth:'thin', scrollbarColor:'#3a2808 transparent',
          }}>
            <div style={{ display:'flex', gap:14, paddingBottom:0, minWidth:'max-content', alignItems:'flex-end' }}>
              {archetypes.map((arch, i) => (
                <ArchCard
                  key={arch.id}
                  arch={arch}
                  index={i}
                  isSelected={selectedId === arch.id}
                  onClick={() => selectArchetype(arch.id)}
                />
              ))}
              <NewCard onClick={() => selectArchetype(null)} />
            </div>
          </div>

          {/* ── Connector ── */}
          <div style={{ padding:'0 2.5rem', paddingLeft: selectedId !== null
            ? `calc(2.5rem + ${archetypes.findIndex(a => a.id === selectedId) * 122 + 54}px)`
            : 'calc(2.5rem + 40px)'
          }}>
            <div style={{ height:20, display:'flex', alignItems:'flex-end', gap:0 }}>
              <div style={{ width:1, height:'100%', background:'linear-gradient(to bottom, var(--th-gold), rgba(201,160,64,.1))' }} />
              <div style={{ width:7, height:7, border:'1px solid var(--th-gold)', transform:'rotate(45deg)', background:'var(--th-bg,#0a0804)', boxShadow:'0 0 8px var(--th-gold-glow)', marginLeft:-3, marginBottom:-3 }} />
            </div>
          </div>

          {/* ── Scroll Panel ── */}
          <div style={{ padding:'0 2.5rem 2.5rem' }}>
            <div style={{
              position:'relative',
              background:'linear-gradient(160deg,#171008 0%,#100c06 50%,#0d0903 100%)',
              border:'1px solid #3a2808', borderTop:'none',
              boxShadow:'0 0 0 1px rgba(201,160,64,.07), 0 24px 60px rgba(0,0,0,.8), inset 0 1px 0 rgba(201,160,64,.04)',
              overflow:'hidden',
            }}>
              {/* ambient glow */}
              <div style={{ position:'absolute', top:-40, left:'50%', transform:'translateX(-50%)', width:'60%', height:80, background:'radial-gradient(ellipse, rgba(201,160,64,.05) 0%, transparent 70%)', pointerEvents:'none' }} />

              {/* gold top bar */}
              <div style={{ height:2, background:'linear-gradient(to right, transparent 0%, var(--th-gold-dk,#8a6020) 20%, var(--th-gold) 50%, var(--th-gold-dk,#8a6020) 80%, transparent 100%)', boxShadow:'0 0 12px rgba(201,160,64,.4), 0 0 24px rgba(201,160,64,.15)' }} />

              {/* Header */}
              <div style={{
                display:'flex', alignItems:'center', gap:'1.2rem',
                padding:'1.1rem 1.8rem', borderBottom:'1px solid #1e1206', position:'relative',
              }}>
                <div style={{ position:'absolute', bottom:-1, left:'10%', right:'10%', height:1, background:'linear-gradient(to right, transparent, #3a2808, transparent)' }} />
                <span style={{
                  fontSize:38, lineHeight:1,
                  filter:'drop-shadow(0 4px 8px rgba(0,0,0,.9)) drop-shadow(0 0 16px rgba(201,160,64,.22))',
                  animation:'arch-float 4s ease-in-out infinite',
                }}>
                  {loading ? '⌛' : editor.ikon}
                </span>
                <div>
                  <div style={{ fontFamily:'var(--font-display)', fontSize:'1.25rem', fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase', color:'var(--th-gold)', textShadow:'0 0 20px rgba(201,160,64,.2), 0 2px 4px rgba(0,0,0,.6)', lineHeight:1 }}>
                    {isNew ? 'Új Archetípus' : editor.nev || '—'}
                  </div>
                  <div style={{ fontStyle:'italic', fontSize:'0.88rem', color:'var(--th-faint)', marginTop:'0.2rem' }}>
                    {isNew ? 'Add meg a nevet és válassz ikont' : editor.leiras || 'Leírás nincs megadva'}
                  </div>
                </div>
              </div>

              {/* Fields + Icon Picker */}
              <div style={{ padding:'1.2rem 1.8rem', display:'grid', gridTemplateColumns:'170px 1fr', gap:'1.5rem', borderBottom:'1px solid #1e1206' }}>
                <div>
                  <label style={labelStyle}>Ikon választás</label>
                  <IconPicker value={editor.ikon} onChange={v => updateEditor({ ikon: v })} />
                </div>
                <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
                  <div>
                    <label style={labelStyle}>Megnevezés</label>
                    <input
                      value={editor.nev}
                      onChange={e => updateEditor({ nev: e.target.value })}
                      placeholder="pl. Harcos Elit, Árnyék Tolvaj…"
                      style={{
                        width:'100%', background:'rgba(0,0,0,.35)',
                        border:'none', borderBottom:'1px solid #3a2808',
                        color:'var(--th-gold)', fontFamily:'var(--font-display)',
                        fontSize:'0.95rem', letterSpacing:'0.05em',
                        padding:'0.35rem 0.1rem', outline:'none',
                        transition:'border-color 0.2s',
                      }}
                      onFocus={e => e.target.style.borderBottomColor='var(--th-gold)'}
                      onBlur={e => e.target.style.borderBottomColor='#3a2808'}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Leírás</label>
                    <textarea
                      value={editor.leiras}
                      onChange={e => updateEditor({ leiras: e.target.value })}
                      rows={2}
                      placeholder="Rövid jellemzés…"
                      style={{
                        width:'100%', background:'rgba(0,0,0,.25)',
                        border:'1px solid #2a1a04', color:'var(--th-text)',
                        fontFamily:'var(--font-lore)', fontStyle:'italic',
                        fontSize:'0.9rem', padding:'0.5rem 0.7rem',
                        outline:'none', resize:'none', lineHeight:1.6,
                        transition:'border-color 0.2s',
                      }}
                      onFocus={e => e.target.style.borderColor='#3a2808'}
                      onBlur={e => e.target.style.borderColor='#2a1a04'}
                    />
                  </div>
                </div>
              </div>

              {/* Rune divider */}
              <div style={{ display:'flex', alignItems:'center', gap:'0.75rem', padding:'0.6rem 1.8rem' }}>
                <div style={{ flex:1, height:1, background:'linear-gradient(to right, transparent, #2a1a04)' }} />
                <span style={{ color:'#2a1a04', fontSize:'0.7rem', letterSpacing:'0.3em' }}>ᚱ ᚢ ᚾ ᛖ</span>
                <div style={{ flex:1, height:1, background:'linear-gradient(to left, transparent, #2a1a04)' }} />
              </div>

              {/* Skill list */}
              <div style={{ padding:'0 1.8rem 0.6rem' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'0.75rem', marginBottom:'0.8rem' }}>
                  <span style={{ fontFamily:'var(--font-display)', fontSize:'0.6rem', letterSpacing:'0.18em', textTransform:'uppercase', color:'var(--th-faint)', whiteSpace:'nowrap' }}>
                    Képzettségek prioritás szerint
                  </span>
                  <div style={{ flex:1, height:1, background:'linear-gradient(to right, #2a1a04, transparent)' }} />
                  <span style={{ fontStyle:'italic', fontSize:'0.75rem', color:'var(--th-faint)' }}>
                    {editor.kepzettsegek.length} tétel
                  </span>
                </div>

                {editor.kepzettsegek.length === 0 ? (
                  <p style={{ fontStyle:'italic', fontSize:'0.82rem', color:'var(--th-faint)', padding:'0.3rem 0' }}>
                    Még nincs képzettség. Add hozzá alul.
                  </p>
                ) : (
                  editor.kepzettsegek.map((item, i) => (
                    <SkillRow
                      key={`${item.kepzettseg_id}-${i}`}
                      item={item} index={i} total={editor.kepzettsegek.length}
                      allSkills={allSkills}
                      onChange={updated => changeSkill(i, updated)}
                      onMoveUp={() => moveSkill(i, -1)}
                      onMoveDown={() => moveSkill(i, 1)}
                      onRemove={() => removeSkill(i)}
                    />
                  ))
                )}

                <AddSkillRow allSkills={allSkills} existingIds={existingIds} onAdd={addSkill} />
              </div>

              {/* Action bar */}
              <div style={{
                display:'flex', alignItems:'center', gap:'0.75rem',
                padding:'0.85rem 1.8rem', borderTop:'1px solid #1e1206',
                background:'rgba(0,0,0,.25)', position:'relative',
              }}>
                <div style={{ position:'absolute', top:-1, left:'10%', right:'10%', height:1, background:'linear-gradient(to right, transparent, #3a2808, transparent)' }} />

                <button
                  onClick={handleSave}
                  disabled={saving || !dirty}
                  style={{
                    fontFamily:'var(--font-display)', fontSize:'0.68rem',
                    letterSpacing:'0.14em', textTransform:'uppercase',
                    background:'rgba(122,30,30,.2)', border:'1px solid var(--th-accent)',
                    color:'#d06060', padding:'0.5rem 1.4rem',
                    cursor: (saving || !dirty) ? 'not-allowed' : 'pointer',
                    opacity: (saving || !dirty) ? 0.45 : 1,
                    display:'flex', alignItems:'center', gap:'0.5rem',
                    transition:'all 0.2s', outline:'none',
                    boxShadow:'inset 0 1px 0 rgba(255,255,255,.04)',
                  }}
                  onMouseEnter={e => { if (!saving && dirty) { e.currentTarget.style.background='rgba(122,30,30,.38)'; e.currentTarget.style.boxShadow='0 0 16px rgba(122,30,30,.3), inset 0 1px 0 rgba(255,255,255,.04)'; e.currentTarget.style.transform='translateY(-1px)' }}}
                  onMouseLeave={e => { e.currentTarget.style.background='rgba(122,30,30,.2)'; e.currentTarget.style.boxShadow='inset 0 1px 0 rgba(255,255,255,.04)'; e.currentTarget.style.transform='none' }}
                >
                  {saving
                    ? <Spinner size={14} />
                    : <span style={{ animation:'arch-seal-rotate 8s linear infinite', display:'inline-block' }}>✦</span>
                  }
                  {isNew ? 'Létrehozás' : 'Pecsételés'}
                </button>

                {dirty && (
                  <span style={{ display:'flex', alignItems:'center', gap:'0.35rem', fontSize:'0.7rem', fontStyle:'italic', color:'var(--th-faint)', animation:'arch-dirty-in 0.3s ease' }}>
                    <span style={{ width:6, height:6, borderRadius:'50%', background:'var(--th-gold)', boxShadow:'0 0 6px var(--th-gold-glow)', animation:'arch-pulse-glow 2s ease-in-out infinite', display:'inline-block' }} />
                    nem mentett
                  </span>
                )}

                {!isNew && (
                  <button
                    onClick={handleDelete}
                    disabled={saving}
                    style={{
                      marginLeft:'auto',
                      fontFamily:'var(--font-display)', fontSize:'0.63rem',
                      letterSpacing:'0.1em', textTransform:'uppercase',
                      background:'transparent', border:'1px solid #2a1a04',
                      color:'var(--th-faint)', padding:'0.45rem 1rem',
                      cursor: saving ? 'not-allowed' : 'pointer',
                      transition:'all 0.2s', outline:'none',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor='var(--th-accent)'; e.currentTarget.style.color='var(--th-danger)'; e.currentTarget.style.background='rgba(122,30,30,.08)' }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor='#2a1a04'; e.currentTarget.style.color='var(--th-faint)'; e.currentTarget.style.background='transparent' }}
                  >Törlés</button>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

const labelStyle = {
  fontFamily:'var(--font-display)',
  fontSize:'0.57rem',
  letterSpacing:'0.18em',
  textTransform:'uppercase',
  color:'var(--th-faint)',
  display:'block',
  marginBottom:'0.4rem',
}
