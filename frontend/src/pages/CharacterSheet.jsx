import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getKarakter } from '../api/magus'
import Spinner from '../components/ui/Spinner'

const PROPS_ORDER = [
  'ero', 'gyorsasag', 'ugyesseg', 'allokepesseg',
  'egeszseg', 'szepseg', 'intelligencia', 'akarateroe', 'asztral', 'erzekeles',
]
const PROP_LABEL = {
  ero: 'Erő', gyorsasag: 'Gyorsaság', ugyesseg: 'Ügyesség',
  allokepesseg: 'Állóképesség', egeszseg: 'Egészség', szepseg: 'Szépség',
  intelligencia: 'Intelligencia', 'akarateroe': 'Akaraterő',
  asztral: 'Asztrál', erzekeles: 'Érzékelés',
}

const BD  = '1px solid #1a1a1a'
const SF  = { fontFamily: 'Georgia, "Times New Roman", serif' }
const SFB = { ...SF, fontWeight: 'bold' }

// ── Atomic building blocks ────────────────────────────────────────────────────

function PropRow({ label, value }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '1.5px 0', gap: 4 }}>
      <span style={{ flex: 1, fontSize: '0.78rem', ...SF }}>{label}</span>
      <div style={{ width: 30, border: BD, textAlign: 'center', fontSize: '0.85rem', lineHeight: '1.4', ...SFB }}>
        {value ?? ''}
      </div>
    </div>
  )
}

function LabeledBox({ label, value, flex, style }) {
  return (
    <div style={{ border: BD, padding: '1px 3px', flex, ...style }}>
      <div style={{ fontSize: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.04em', lineHeight: 1.3, color: '#333' }}>{label}</div>
      <div style={{ fontSize: '0.78rem', minHeight: '1em', ...SFB }}>{value ?? ''}</div>
    </div>
  )
}

function SectionHeader({ children }) {
  return (
    <div style={{
      ...SFB, fontSize: '0.62rem', textAlign: 'center', letterSpacing: '0.06em',
      textTransform: 'uppercase', padding: '2px 4px', borderBottom: BD,
    }}>
      {children}
    </div>
  )
}

function FieldLine({ label, value, style }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', borderBottom: '1px solid #888', marginBottom: 2, paddingBottom: 1, ...style }}>
      <span style={{ fontSize: '0.7rem', ...SFB, whiteSpace: 'nowrap', marginRight: 4 }}>{label}</span>
      <span style={{ flex: 1, fontSize: '0.8rem', ...SF }}>{value ?? ''}</span>
    </div>
  )
}

function BlankLines({ n = 3 }) {
  return Array.from({ length: n }, (_, i) => (
    <div key={i} style={{ borderBottom: '1px solid #aaa', marginBottom: 4, minHeight: '1em' }} />
  ))
}

// ── Section: one combat value block (KÉ / TÉ / VÉ / CÉ) ────────────────────

function CombatBlock({ title, pancelnelkul, alap }) {
  return (
    <div style={{ border: BD, marginBottom: 3 }}>
      <SectionHeader>{title}</SectionHeader>
      <div style={{ padding: '3px 4px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        <div style={{ display: 'flex', gap: 3 }}>
          <LabeledBox label="Páncélban"     value={undefined}    flex={1} />
          <LabeledBox label="Páncél nélkül" value={pancelnelkul} flex={1} />
        </div>
        <div style={{ display: 'flex', gap: 3 }}>
          <LabeledBox label="Alap"           value={alap}      flex={1} />
          <LabeledBox label="Fegyver nélkül" value={undefined} flex={1} />
        </div>
        <LabeledBox label="Módosítók" value={undefined} />
      </div>
    </div>
  )
}

// ── Page 1 ────────────────────────────────────────────────────────────────────

function Page1({ char, sb, combat }) {
  const props = sb.stats || {}

  // Concatenate narrative for "A Karakter leírása" field
  const leiras = [
    char.appearance && `Megjelenés: ${char.appearance}`,
    char.personality && `Személyiség: ${char.personality}`,
    char.motivation && `Motiváció: ${char.motivation}`,
    char.speech_style && `Szólásmod: ${char.speech_style}`,
  ].filter(Boolean).join('\n\n')

  return (
    <div>
      {/* Title */}
      <div style={{
        textAlign: 'center', fontSize: '2rem', ...SFB,
        color: '#5c1010', letterSpacing: '0.12em', textTransform: 'uppercase',
        marginBottom: 8, borderBottom: '2px solid #5c1010', paddingBottom: 4,
      }}>
        M.A.G.U.S. KARAKTERLAP
      </div>

      {/* 3-column main body */}
      <div style={{ display: 'grid', gridTemplateColumns: '26% 38% 36%', gap: 4, marginBottom: 4 }}>

        {/* ── Left column: properties + psi + mana ─────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>

          {/* Properties */}
          <div style={{ border: BD, padding: '3px 5px' }}>
            {PROPS_ORDER.map(p => (
              <PropRow key={p} label={PROP_LABEL[p]} value={props[p]} />
            ))}
            <div style={{ display: 'flex', alignItems: 'center', marginTop: 3, gap: 4 }}>
              <span style={{ fontSize: '0.6rem', ...SFB }}>Sebzés járulék</span>
              <div style={{ flex: 1, border: BD, height: '1.3em' }} />
            </div>
          </div>

          {/* Ψ-képzettség */}
          <div style={{ border: BD }}>
            <SectionHeader>Ψ-képzettség</SectionHeader>
            <div style={{ padding: '3px 5px', display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FieldLine label="Iskola típusa" />
              <FieldLine label="Használat foka" />
              <FieldLine label="Használat szintje" />
              <div style={{ display: 'flex', gap: 3, marginTop: 2 }}>
                <LabeledBox label="Akt. Ψp"  flex={1} />
                <LabeledBox label="Max. Ψp"  flex={1} />
              </div>
              <LabeledBox label="Ψp/Szint" style={{ marginTop: 2 }} />
            </div>
          </div>

          {/* Ψ-pajzsok */}
          <div style={{ border: BD }}>
            <SectionHeader>Ψ-pajzsok</SectionHeader>
            <div style={{ padding: '3px 5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: 2 }}>
                <span style={{ fontSize: '0.6rem', ...SFB }}>ASZTRÁL</span>
                <span style={{ fontSize: '0.6rem', ...SFB }}>MENTÁL</span>
              </div>
              {['Statikus', 'Dinamikus', 'ME'].map(r => (
                <div key={r} style={{ display: 'flex', gap: 3, marginBottom: 2 }}>
                  <LabeledBox label={r} flex={1} />
                  <LabeledBox label={r} flex={1} />
                </div>
              ))}
            </div>
          </div>

          {/* Mana-pontok */}
          <div style={{ border: BD, flex: 1 }}>
            <SectionHeader>Mana-pontok</SectionHeader>
            <div style={{ padding: '3px 5px', display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ display: 'flex', gap: 3 }}>
                <LabeledBox label="Mp/Szint" flex={1} />
                <LabeledBox label="Max. Mp"  flex={1} />
              </div>
              <LabeledBox label="Akt. Mp" />
              <div style={{ marginTop: 3 }}>
                <span style={{ fontSize: '0.6rem', ...SFB }}>Egyéb módosítók</span>
                <BlankLines n={4} />
              </div>
            </div>
          </div>
        </div>

        {/* ── Middle column: vitals + identity ─────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>

          {/* Életerő */}
          <div style={{ border: BD }}>
            <SectionHeader>Életerő</SectionHeader>
            <div style={{ padding: '3px 5px', display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ display: 'flex', gap: 3 }}>
                <LabeledBox label="Max. Ép" value={combat.ep} flex={1} />
                <LabeledBox label="Max. Fp" value={combat.fp} flex={1} />
              </div>
              <div style={{ display: 'flex', gap: 3 }}>
                <LabeledBox label="Akt. Ép"  flex={1} />
                <LabeledBox label="Fp/Szint" value={combat.fp_formula} flex={1} />
              </div>
              <LabeledBox label="Akt. Fp" />
            </div>
          </div>

          {/* Karakter neve + identity fields */}
          <div style={{ border: BD, padding: '4px 6px', display: 'flex', flexDirection: 'column', gap: 2 }}>
            <div style={{ textAlign: 'center', fontSize: '0.65rem', ...SFB, marginBottom: 2 }}>A Karakter neve</div>
            <FieldLine label=""     value={char.name} style={{ borderBottom: '2px solid #1a1a1a', marginBottom: 4 }} />
            <FieldLine label="Kaszt"     value={sb.class} />
            <FieldLine label="Faj"       value={sb.race} />
            <FieldLine label="Jellem" />
            <FieldLine label="Vallás" />
            <FieldLine label="Szimbólum" />
            <FieldLine label="Szülőföld" />
            <FieldLine label="Iskola" />
          </div>

          {/* Portrait area */}
          <div style={{
            border: BD, flex: 1, minHeight: 80,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {char.gender && char.age_description && (
              <span style={{ fontSize: '0.7rem', color: '#888', ...SF, fontStyle: 'italic' }}>
                {char.gender}, {char.age_description}
              </span>
            )}
          </div>

          {/* Tapasztalati Szint */}
          <div style={{ border: BD, padding: '4px 6px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.65rem', ...SFB, marginBottom: 2 }}>Tapasztalati Szint</div>
            <div style={{ fontSize: '1.8rem', ...SFB, lineHeight: 1 }}>{sb.level ?? ''}</div>
          </div>
        </div>

        {/* ── Right column: combat values ───────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <CombatBlock title="Kezdeményező Érték (KÉ)" pancelnelkul={combat.ke} />
          <CombatBlock title="Támadó Érték (TÉ)"       pancelnelkul={combat.te} />
          <CombatBlock title="Védő Érték (VÉ)"         pancelnelkul={combat.ve} />
          <CombatBlock title="Célzó Érték (CÉ)"        pancelnelkul={combat.ce} />

          <div style={{ border: BD, padding: '3px 4px', display: 'flex', gap: 3, marginTop: 'auto' }}>
            <LabeledBox label="HM/Szint"  value={combat.szabad_hm_per_szint} flex={1} />
            <LabeledBox label="Tám./kör"  flex={1} />
          </div>
        </div>
      </div>

      {/* ── Armor row ────────────────────────────────────────────────── */}
      <div style={{ border: BD, display: 'flex', gap: 0, marginBottom: 3 }}>
        <LabeledBox label="Viselt páncél" style={{ flex: 3, borderRight: BD }} />
        <LabeledBox label="MGT"      style={{ flex: 1, borderRight: BD }} />
        <LabeledBox label="Max. SFÉ" style={{ flex: 1, borderRight: BD }} />
        <LabeledBox label="SFÉ"      style={{ flex: 1, borderRight: BD }} />
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
          <LabeledBox label="Pajzs"    style={{ borderBottom: BD }} />
          <LabeledBox label="Pajzs VÉ" style={{ borderBottom: BD }} />
          <LabeledBox label="Sebzés" />
        </div>
      </div>

      {/* ── Weapons table ─────────────────────────────────────────────── */}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.72rem', ...SF }}>
        <thead>
          <tr>
            {['Fegyver', 'Tám/kör', 'KÉ', 'TÉ', 'VÉ', 'Sebzés'].map((h, i) => (
              <th key={h} style={{
                border: BD, padding: '2px 4px', ...SFB, fontSize: '0.62rem',
                textAlign: 'center', background: '#f5f0eb',
                width: i === 0 ? '35%' : i === 5 ? '20%' : undefined,
              }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 8 }, (_, i) => (
            <tr key={i}>
              {Array.from({ length: 6 }, (_, j) => (
                <td key={j} style={{ border: BD, height: '1.5em', padding: '1px 3px' }} />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Page 2 ────────────────────────────────────────────────────────────────────

function Page2({ char, sb, combat, karakter, kepzettsegek = [] }) {
  const leiras = [
    char.appearance  && `Megjelenés: ${char.appearance}`,
    char.personality && `Személyiség: ${char.personality}`,
    char.background  && `Háttér: ${char.background}`,
    char.motivation  && `Motiváció: ${char.motivation}`,
    char.speech_style && `Szólásmod: ${char.speech_style}`,
    char.secret      && `Titok: ${char.secret}`,
  ].filter(Boolean).join('\n\n')

  const felszereles  = karakter.felszereles || []
  const celok        = karakter.celok || []
  const manySkills   = kepzettsegek.length > 28
  const equipRows    = manySkills ? 7 : 14

  return (
    <div>
      {/* Skill points header */}
      <div style={{ border: BD, display: 'flex', gap: 0, marginBottom: 4 }}>
        <div style={{ borderRight: BD, padding: '3px 6px', minWidth: 90 }}>
          <div style={{ fontSize: '0.6rem', ...SFB }}>Képzettség Pontok</div>
          <div style={{ fontSize: '0.9rem', ...SFB }}>{combat.kp ?? ''}</div>
        </div>
        <LabeledBox label="Kp/Szint" value={combat.kp_per_szint} style={{ borderRight: BD, minWidth: 60 }} />
        <div style={{ flex: 1, padding: '3px 6px' }}>
          <div style={{ fontSize: '0.6rem', ...SFB, marginBottom: 2 }}>Egyéb módosítók</div>
          <BlankLines n={2} />
        </div>
      </div>

      {/* Skills table — 2 or 3 columns depending on skill count */}
      {(() => {
        const ueBonus   = Math.max(0, (sb.stats?.ugyesseg ?? 10) - 10)
        const amSkills  = kepzettsegek.filter(k => k.tipus === 'alap_mester')
        const pctSkills = kepzettsegek.filter(k => k.tipus === 'szazalekos')
        const total     = kepzettsegek.length

        const NUM_COLS = total > 28 ? 3 : 2
        const ROWS     = Math.max(total > 28 ? 13 : 14, Math.ceil((total + 2) / NUM_COLS))
        const TOTAL    = ROWS * NUM_COLS

        const slots = Array(TOTAL).fill(null)
        amSkills.forEach((s, i)  => { if (i < TOTAL) slots[i] = s })
        pctSkills.forEach((s, i) => {
          const idx = TOTAL - 1 - i
          if (idx >= 0 && slots[idx] === null) slots[idx] = s
        })
        const colSlices = Array.from({ length: NUM_COLS }, (_, ci) =>
          slots.slice(ci * ROWS, (ci + 1) * ROWS)
        )

        const nameFontSize = NUM_COLS === 3 ? '0.6rem' : '0.68rem'
        const gridCols     = NUM_COLS === 3 ? '1fr 1fr 1fr' : '1fr 1fr'

        return (
          <div style={{ display: 'grid', gridTemplateColumns: gridCols, gap: 3, marginBottom: 4 }}>
            {colSlices.map((col, ci) => (
              <table key={ci} style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.68rem', ...SF }}>
                <thead>
                  <tr>
                    {['Képzettség', 'Kp', 'Fok'].map(h => (
                      <th key={h} style={{
                        border: BD, padding: '1px 3px', ...SFB, fontSize: '0.58rem',
                        textAlign: 'center', background: '#f5f0eb',
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {col.map((s, i) => {
                    const pct = s?.tipus === 'szazalekos' ? (s.szazalek ?? 0) + ueBonus : null
                    const fok = s ? (s.tipus === 'szazalekos' ? `${pct}%` : s.fok) : ''
                    return (
                      <tr key={i}>
                        <td style={{ border: BD, height: '1.35em', padding: '1px 3px', width: '58%', fontSize: nameFontSize, ...SF }}>
                          {s?.nev ?? ''}
                        </td>
                        <td style={{ border: BD, padding: '1px 3px', width: '20%', textAlign: 'center', fontSize: '0.62rem' }} />
                        <td style={{ border: BD, padding: '1px 3px', width: '22%', textAlign: 'center', fontSize: '0.58rem', ...SF }}>
                          {fok}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            ))}
          </div>
        )
      })()}

      {/* Kincsek */}
      <div style={{ border: BD, marginBottom: 4 }}>
        <SectionHeader>Kincsek</SectionHeader>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 0 }}>
          {['réz', 'ezüst', 'arany', 'mithrill', 'drágakő', 'egyéb'].map((k, i) => (
            <LabeledBox key={k} label={k} style={{ borderRight: i < 5 ? BD : undefined, minHeight: 32 }} />
          ))}
        </div>
      </div>

      {/* Equipment — two columns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4, marginBottom: 4 }}>
        {[0, 1].map(col => (
          <table key={col} style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.7rem', ...SF }}>
            <thead>
              <tr>
                {['Felszerelés', 'Darab', 'Elhelyezés'].map(h => (
                  <th key={h} style={{
                    border: BD, padding: '2px 4px', ...SFB, fontSize: '0.6rem',
                    textAlign: 'center', background: '#f5f0eb',
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: equipRows }, (_, i) => {
                const item = col === 0 ? felszereles[i] : felszereles[equipRows + i]
                return (
                  <tr key={i}>
                    <td style={{ border: BD, height: '1.4em', padding: '1px 3px', width: '55%', fontSize: '0.72rem', ...SF }}>
                      {item?.nev ?? ''}
                    </td>
                    <td style={{ border: BD, padding: '1px 3px', width: '15%', textAlign: 'center', fontSize: '0.72rem' }}>
                      {item?.db ?? ''}
                    </td>
                    <td style={{ border: BD, padding: '1px 3px', width: '30%', fontSize: '0.72rem', ...SF }}>
                      {item?.hely ?? ''}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        ))}
      </div>

      {/* Bottom: notes + description + XP */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr', gap: 4 }}>
        <div style={{ border: BD, padding: '4px 6px' }}>
          <div style={{ fontSize: '0.6rem', ...SFB, marginBottom: 4 }}>Egyéb módosítók</div>
          {celok.length > 0
            ? celok.map((c, i) => (
                <div key={i} style={{ fontSize: '0.72rem', ...SF, marginBottom: 2, borderBottom: '1px solid #ccc' }}>{c}</div>
              ))
            : <BlankLines n={5} />
          }
        </div>
        <div style={{ border: BD, padding: '4px 6px' }}>
          <div style={{ fontSize: '0.6rem', ...SFB, marginBottom: 4 }}>A Karakter leírása</div>
          <div style={{ fontSize: '0.72rem', ...SF, whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
            {leiras || ''}
          </div>
        </div>
        <div style={{ border: BD, padding: '4px 6px' }}>
          <div style={{ fontSize: '0.6rem', ...SFB, marginBottom: 4 }}>Tapasztalati Pontok</div>
          <BlankLines n={2} />
          <div style={{ fontSize: '0.6rem', ...SFB, marginTop: 8, marginBottom: 4 }}>Pontok a következő szinthez</div>
          <BlankLines n={2} />
        </div>
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

const PRINT_STYLE = `
  @media print {
    @page { size: A4 portrait; margin: 7mm; }
    body > * { display: none !important; }
    #character-sheet-root { display: block !important; }
    .no-print { display: none !important; }
    .sheet-page { box-shadow: none !important; page-break-after: always; }
    .sheet-page:last-child { page-break-after: avoid; }
  }
`

export default function CharacterSheet() {
  const { id }   = useParams()
  const navigate = useNavigate()
  const [karakter, setKarakter] = useState(null)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)

  useEffect(() => {
    getKarakter(Number(id))
      .then(setKarakter)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Spinner /></div>
  if (error)   return <div style={{ padding: 40, color: 'red' }}>Hiba: {error}</div>
  if (!karakter) return null

  const char         = karakter.character || {}
  const sb           = karakter.stat_block || {}
  const combat       = sb.combat || {}
  const kepzettsegek = karakter.kepzettsegek || []

  const pageStyle = {
    background: '#fff',
    color: '#000',
    width: '210mm',
    minHeight: '297mm',
    margin: '0 auto 8mm',
    padding: '8mm',
    boxSizing: 'border-box',
    boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
    fontSize: '10px',
  }

  return (
    <>
      <style>{PRINT_STYLE}</style>

      <div id="character-sheet-root">
        {/* Print controls */}
        <div className="no-print" style={{
          position: 'sticky', top: 0, zIndex: 100,
          background: '#1a1a2e', padding: '8px 16px',
          display: 'flex', gap: 8, alignItems: 'center',
          borderBottom: '2px solid #c8a84b',
        }}>
          <button
            onClick={() => window.print()}
            style={{
              background: '#c8a84b', color: '#1a1a2e', border: 'none',
              padding: '6px 16px', cursor: 'pointer', fontWeight: 'bold',
              fontSize: '0.85rem', letterSpacing: '0.05em',
            }}
          >
            🖨 Nyomtatás / PDF
          </button>
          <button
            onClick={() => navigate(-1)}
            style={{
              background: 'transparent', color: '#c8a84b', border: '1px solid #c8a84b',
              padding: '5px 12px', cursor: 'pointer', fontSize: '0.85rem',
            }}
          >
            ← Vissza
          </button>
          <span style={{ color: '#aaa', fontSize: '0.8rem', marginLeft: 8 }}>
            {char.name ?? 'Névtelen'} · {sb.class} {sb.level}. szint
          </span>
        </div>

        <div style={{ padding: '16px 0', background: '#e8e0d0' }}>
          {/* Page 1 */}
          <div className="sheet-page" style={pageStyle}>
            <Page1 char={char} sb={sb} combat={combat} />
          </div>

          {/* Page 2 */}
          <div className="sheet-page" style={pageStyle}>
            <Page2 char={char} sb={sb} combat={combat} karakter={karakter} kepzettsegek={kepzettsegek} />
          </div>
        </div>
      </div>
    </>
  )
}
