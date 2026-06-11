# NPC Generator Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle `frontend/src/pages/NpcGenerator.jsx` ("NPC Generálás") to match the "Field Dossier" dark-fantasy ledger design approved in `docs/superpowers/specs/2026-06-10-npc-generator-redesign.md`.

**Architecture:** Single-file frontend change, no new components or CSS. Replace the shared `<Header>` with bespoke ledger-style header markup (eyebrow, gold title, floating `†`, pulsing gold underline). Restyle the input panel using the existing `.archive-panel`/`.archive-panel-gold` classes, turn the example-role buttons into ledger pills, add a rotating seal icon to the Generate button, and insert `<RuneDivider symbol="⬥" />` between the input panel and results. In the generated dossier: add a gold glow to the NPC name, replace the old 3-column "Harci értékek" combat box with a horizontal vitals bar (KÉ/TÉ/VÉ/CÉ/ÉP/FP), switch the left narrative column from `.paper-card` to `.archive-panel`, and fix `StatRow`/`DossierField`/speech-quote colors that were tuned for parchment but used on dark backgrounds.

**Tech Stack:** React 18 (Vite), inline-style components (no CSS modules/Tailwind for page-level styling), CSS custom properties and keyframes already defined in `frontend/src/index.css` (`.archive-panel`, `.archive-panel-gold`, `.rune-divider`, `arch-float`, `arch-pulse-glow`, `arch-seal-rotate`).

---

### Task 1: Header replacement + dark-panel color fixes (StatRow, DossierField, speech quote)

**Files:**
- Modify: `frontend/src/pages/NpcGenerator.jsx` (imports at lines 1-7, `DossierField` at lines 15-44, `StatRow` at lines 46-71, speech-style quote at lines 146-160, page header at lines 350-357)

- [ ] **Step 1: Remove the now-unused shared `Header` import**

In `frontend/src/pages/NpcGenerator.jsx`, find:

```jsx
import { useState } from 'react'
import Header from '../components/layout/Header'
import Button from '../components/ui/Button'
```

Replace with:

```jsx
import { useState } from 'react'
import Button from '../components/ui/Button'
```

- [ ] **Step 2: Recolor `DossierField` body text for dark backgrounds**

Find:

```jsx
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
```

Replace with:

```jsx
      <p
        style={{
          fontSize: '0.9rem',
          color: 'var(--th-text)',
          fontFamily: 'var(--font-lore)',
          lineHeight: 1.6,
          margin: 0,
        }}
      >
        {children}
      </p>
```

- [ ] **Step 3: Fix `StatRow` border, label and value colors**

`StatRow` is rendered exclusively on dark `.archive-panel` backgrounds, but its colors
(`--th-ink-muted`, `--th-ink`, `rgba(0,0,0,0.1)` border) are tuned for parchment and are
nearly invisible on dark surfaces. Find:

```jsx
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
```

Replace with:

```jsx
function StatRow({ label, value }) {
  if (value == null) return null
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0.2rem 0',
        borderBottom: '1px solid var(--th-border)',
      }}
    >
      <span
        style={{
          fontSize: '0.68rem',
          color: 'var(--th-muted)',
          fontFamily: 'var(--font-display)',
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
        }}
      >
        {label}
      </span>
      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--th-gold-lt)' }}>{value}</span>
    </div>
  )
}
```

- [ ] **Step 4: Recolor the speech-style quote**

Find:

```jsx
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
```

Replace with:

```jsx
          {char.speech_style && (
            <p
              style={{
                fontSize: '0.88rem',
                color: 'var(--th-muted)',
                fontFamily: 'var(--font-lore)',
                fontStyle: 'italic',
                margin: '0 0 0.75rem',
                paddingLeft: '0.75rem',
                borderLeft: '2px solid var(--th-border-strong)',
              }}
            >
              „{char.speech_style}"
            </p>
          )}
```

- [ ] **Step 5: Replace the shared `<Header>` with a bespoke "Command Ledger" header**

Find:

```jsx
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <Header
        title="NPC Generálás"
        subtitle="Önálló karakter létrehozása — faj, kaszt és szint automatikus meghatározással"
      />

      <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
```

Replace with:

```jsx
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          padding: '1.25rem 2rem 1rem',
          borderBottom: '1px solid var(--th-border)',
          background: 'var(--th-surface)',
          position: 'relative',
        }}
      >
        <p
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '0.62rem',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'var(--th-faint)',
            margin: '0 0 0.15rem',
          }}
        >
          MAGUS · Mesélői Eszközök
        </p>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1rem',
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--th-gold)',
              margin: 0,
            }}
          >
            NPC Generálás
          </h2>
          <span
            style={{
              fontSize: '1.1rem',
              color: 'var(--th-gold)',
              animation: 'arch-float 4s ease-in-out infinite',
            }}
          >
            †
          </span>
        </div>
        <p
          style={{
            margin: '0.2rem 0 0',
            fontSize: '0.85rem',
            color: 'var(--th-faint)',
            fontFamily: 'var(--font-lore)',
            fontStyle: 'italic',
          }}
        >
          Önálló karakter létrehozása — faj, kaszt és szint automatikus meghatározással
        </p>
        <div
          style={{
            position: 'absolute',
            bottom: '-1px',
            left: '2rem',
            width: '25%',
            height: '2px',
            background: 'var(--th-gold)',
            animation: 'arch-pulse-glow 2.5s ease-in-out infinite',
          }}
        />
      </header>

      <div style={{ padding: '1.5rem 2rem', flex: 1 }}>
```

Note: the spec says `left: 0` for the underline; this plan uses `left: '2rem'` so the
underline aligns under the title text instead of under the header's left padding
(absolutely-positioned children are positioned against the padding box, so `left: 0`
would sit flush with the header's outer edge, to the left of the title).

- [ ] **Step 6: Build verification**

Run from the `frontend/` directory:

```bash
cd frontend && npm run build
```

Expected: build completes with no errors (warnings about chunk size are pre-existing
and OK).

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/NpcGenerator.jsx
git commit -m "Redesign NPC generator header and fix dark-panel text colors"
```

---

### Task 2: Input panel restyle (archive-panel, ledger pills, seal icon) + RuneDivider

**Files:**
- Modify: `frontend/src/pages/NpcGenerator.jsx` (input panel wrapper at lines ~359-370, example-role buttons at lines ~396-422, Generate button at lines ~454-460, divider insertion at line ~461)

- [ ] **Step 1: Convert the input panel wrapper to `.archive-panel.archive-panel-gold`**

Find:

```jsx
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
```

Replace with:

```jsx
        <div
          className="archive-panel archive-panel-gold"
          style={{
            padding: '1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
```

- [ ] **Step 2: Restyle example-role buttons as ledger pills**

The spec calls for Cinzel uppercase 0.62rem tags, but `EXAMPLE_ROLES` holds full
descriptive sentences (e.g. "fogadós — kövér, vidám ember"), which become hard to read
in uppercase Cinzel at that size. This step keeps the existing `font-lore italic`
styling for legibility while applying the spec's ledger-pill border and gold-hover
treatment (border `var(--th-border-strong)`, hover border/text `var(--th-gold)`,
hover background `rgba(176,138,74,0.08)`).

Find:

```jsx
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
```

Replace with:

```jsx
              {EXAMPLE_ROLES.map(r => (
                <button
                  key={r}
                  onClick={() => setRoleHint(r)}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--th-border-strong)',
                    borderRadius: '2px',
                    color: 'var(--th-faint)',
                    fontSize: '0.72rem',
                    padding: '2px 10px',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-lore)',
                    fontStyle: 'italic',
                    transition: 'border-color 0.15s, color 0.15s, background 0.15s',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.color = 'var(--th-gold)'
                    e.currentTarget.style.borderColor = 'var(--th-gold)'
                    e.currentTarget.style.background = 'rgba(176,138,74,0.08)'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.color = 'var(--th-faint)'
                    e.currentTarget.style.borderColor = 'var(--th-border-strong)'
                    e.currentTarget.style.background = 'transparent'
                  }}
                >
                  {r}
                </button>
              ))}
```

- [ ] **Step 3: Add a rotating seal icon to the idle Generate button**

Find:

```jsx
          <Button
            variant="primary"
            onClick={handleGenerate}
            disabled={loading || !roleHint.trim()}
          >
            NPC generálása
          </Button>
```

Replace with:

```jsx
          <Button
            variant="primary"
            onClick={handleGenerate}
            disabled={loading || !roleHint.trim()}
          >
            {!loading && (
              <span
                style={{
                  display: 'inline-block',
                  marginRight: '0.5rem',
                  animation: 'arch-seal-rotate 8s linear infinite',
                }}
              >
                ✦
              </span>
            )}
            NPC generálása
          </Button>
```

- [ ] **Step 4: Insert `<RuneDivider symbol="⬥" />` between the input panel and results**

This also makes use of the previously-unused `RuneDivider` import (line 6). Find:

```jsx
        </div>

        {loading && <Spinner label="NPC generálása..." size={36} />}
```

Replace with:

```jsx
        </div>

        <RuneDivider symbol="⬥" />

        {loading && <Spinner label="NPC generálása..." size={36} />}
```

- [ ] **Step 5: Build verification**

```bash
cd frontend && npm run build
```

Expected: build completes with no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/NpcGenerator.jsx
git commit -m "Restyle NPC generator input panel as ledger archive panel"
```

---

### Task 3: Dossier vitals bar, name glow, archive-panel narrative column

**Files:**
- Modify: `frontend/src/pages/NpcGenerator.jsx` (`NpcResult` function, lines ~73-319: variable setup at line ~79, name heading at lines ~94-105, dossier-header/grid boundary at lines ~126-128, left column wrapper at lines ~130-133, "Combat values" block at lines ~206-275)

- [ ] **Step 1: Compute the `vitals` array from `sb.combat`**

Find:

```jsx
  const char = npc.character ?? {}
  const sb   = npc.stat_block ?? {}
  const conc = npc.concept ?? {}
  const importance = conc.importance ?? 'minor'

  return (
```

Replace with:

```jsx
  const char = npc.character ?? {}
  const sb   = npc.stat_block ?? {}
  const conc = npc.concept ?? {}
  const importance = conc.importance ?? 'minor'

  const vitals = [
    ['KÉ', sb.combat?.ke],
    ['TÉ', sb.combat?.te],
    ['VÉ', sb.combat?.ve],
    ['CÉ', sb.combat?.ce],
    ['ÉP', sb.combat?.ep],
    ['FP', sb.combat?.fp],
  ].filter(([, v]) => v != null)

  return (
```

- [ ] **Step 2: Add a gold glow to the NPC name**

Find:

```jsx
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
```

Replace with:

```jsx
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.4rem',
              letterSpacing: '0.12em',
              color: 'var(--th-gold)',
              margin: '0 0 0.2rem',
              textTransform: 'uppercase',
              textShadow: '0 0 20px var(--th-gold-glow)',
            }}
          >
            {char.name ?? 'Névtelen'}
          </h2>
```

- [ ] **Step 3: Insert the vitals bar between the dossier header and the 2-column body**

Find:

```jsx
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
```

Replace with:

```jsx
        </div>
      </div>

      {vitals.length > 0 && (
        <div
          style={{
            display: 'flex',
            border: '1px solid var(--th-border)',
            borderRadius: '4px',
            overflow: 'hidden',
            background: 'linear-gradient(180deg, var(--th-surface2), var(--th-surface))',
          }}
        >
          {vitals.map(([label, val], i) => (
            <div
              key={label}
              style={{
                flex: 1,
                textAlign: 'center',
                padding: '0.5rem 0.25rem',
                borderRight: i < vitals.length - 1 ? '1px solid var(--th-border)' : 'none',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.05rem',
                  fontWeight: 700,
                  color: 'var(--th-gold)',
                  lineHeight: 1.2,
                }}
              >
                {val}
              </div>
              <div
                style={{
                  fontSize: '0.55rem',
                  fontFamily: 'var(--font-display)',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: 'var(--th-faint)',
                  marginTop: '0.15rem',
                }}
              >
                {label}
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
```

- [ ] **Step 4: Switch the left narrative column from `.paper-card` to `.archive-panel`**

Find:

```jsx
        <div
          className="paper-card"
          style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column' }}
        >
```

Replace with:

```jsx
        <div
          className="archive-panel"
          style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column' }}
        >
```

- [ ] **Step 5: Remove the old "Combat values" (Harci értékek) block**

The vitals bar from Step 3 replaces this block entirely. Find:

```jsx
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
```

Replace with:

```jsx
        {/* Right: stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Attributes */}
```

- [ ] **Step 6: Build verification**

```bash
cd frontend && npm run build
```

Expected: build completes with no errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/NpcGenerator.jsx
git commit -m "Add NPC dossier vitals bar and dark-ledger narrative panel"
```

---

## Manual Verification (after Task 3)

With both servers running (backend on :8000, frontend on :5173 per `CLAUDE.md`):

1. Navigate to `/npc`.
2. Confirm the new header renders: eyebrow line, gold "NPC Generálás" title with a
   floating `†` to its right, italic subtitle, and a pulsing gold underline under the
   title.
3. Confirm the input panel has a 2px gold top border, the example-role pills show the
   gold hover effect, and the Generate button shows a slowly rotating `✦` while idle.
4. Generate an NPC. Confirm:
   - A `⬥` rune divider separates the input panel from the result.
   - The NPC name has a gold glow.
   - A horizontal vitals bar shows KÉ/TÉ/VÉ/CÉ/ÉP/FP with gold values over faint labels.
   - The left column (Megjelenés/Személyiség/Háttér/Motiváció/speech quote/secret) is a
     dark archive panel with legible text (no dark-on-dark contrast issues).
   - The right column ("Tulajdonságok" and "Meta") shows `StatRow` values in legible
     gold-lt text with visible row separators.
5. Toggle "Mesélői titok" open/closed — confirm it still works.
