# Dashboard Redesign (Living Sigil) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current Dashboard (`/`) layout with the approved "Living Sigil" design — a centered rotating-emblem hero with glowing title and count-up stat pills, two accent-colored "portal" action cards, and a vertical timeline of recent saves.

**Architecture:** Single-page React component rewrite (`frontend/src/pages/Dashboard.jsx`) using existing CSS custom properties and animation keyframes from `frontend/src/index.css` (one new keyframe added). Two new small, reusable utility modules: a `useCountUp` hook and a `formatRelativeTime` helper.

**Tech Stack:** React 18, Vite, plain CSS custom properties (no Tailwind/CSS modules for this page, matching existing pages), `react-router-dom` for navigation.

**Reference spec:** `docs/superpowers/specs/2026-06-10-dashboard-redesign.md`

---

## Notes for the engineer

- This codebase has **no frontend test runner** (no vitest/jest configured in `frontend/package.json`). Verification is done via the running dev server (Vite HMR on `http://localhost:5173`) and visual/Playwright checks, matching how the prior `ArchetypeManager` redesign was verified. Do not add a test framework as part of this plan.
- Both servers should already be running per project convention (`uvicorn` on :8000, Vite on :5173). If `http://localhost:5173` doesn't respond, start them per `start-servers.ps1`.
- All theme colors come from CSS custom properties defined in `frontend/src/index.css` under `[data-theme="magus"]` / `[data-theme="starwars"]` — do not hardcode hex colors in the component.
- `theme.icon` is `⚔` for magus and `✦` for starwars (`frontend/src/context/ThemeContext.jsx`).

---

### Task 1: Add `arch-pulse-border` keyframe to index.css

**Files:**
- Modify: `frontend/src/index.css:240-243` (insert after the existing `arch-pulse-glow` block)

- [ ] **Step 1: Add the new keyframe**

In `frontend/src/index.css`, the file currently has this block (around line 240):

```css
@keyframes arch-pulse-glow {
  0%, 100% { opacity: 0.5; box-shadow: 0 0 4px var(--th-gold-glow); }
  50%       { opacity: 1;   box-shadow: 0 0 10px var(--th-gold-glow); }
}
```

Immediately after it (and before `@keyframes arch-seal-rotate`), insert:

```css
@keyframes arch-pulse-border {
  0%, 100% { box-shadow: 0 0 4px var(--th-gold-glow); }
  50%       { box-shadow: 0 0 12px var(--th-gold-glow); }
}
```

This is a box-shadow-only pulse (no opacity change) — used for the Dashboard's
stat pills, where `arch-pulse-glow`'s opacity dip would make the numbers
flicker.

- [ ] **Step 2: Verify no errors**

With the Vite dev server running, request the CSS file and confirm it's served
without error:

```powershell
(Invoke-WebRequest -Uri "http://localhost:5173/src/index.css" -UseBasicParsing).StatusCode
```

Expected: `200`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/index.css
git commit -m "Add arch-pulse-border keyframe for dashboard stat pills"
```

---

### Task 2: Create the `useCountUp` hook

**Files:**
- Create: `frontend/src/hooks/useCountUp.js`

- [ ] **Step 1: Create the hook**

Create `frontend/src/hooks/useCountUp.js`:

```js
import { useState, useEffect, useRef } from 'react'

export function useCountUp(target, duration = 900) {
  const [value, setValue] = useState(0)
  const frameRef = useRef(null)

  useEffect(() => {
    const start = performance.now()

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(target * eased))
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(tick)
      }
    }

    frameRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frameRef.current)
  }, [target, duration])

  return value
}
```

`target` is the final integer value to count up to. `duration` is in
milliseconds. The easing is cubic ease-out (`1 - (1-progress)^3`), so the
count starts fast and settles at the end.

- [ ] **Step 2: Verify**

This hook has no standalone test (no test runner in this project). It's
exercised visually in Task 4, where it drives the Dashboard's stat-pill
numbers — confirm there it counts up from 0 on page load.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/hooks/useCountUp.js
git commit -m "Add useCountUp hook for animated stat numbers"
```

---

### Task 3: Create the `formatRelativeTime` helper

**Files:**
- Create: `frontend/src/utils/time.js`

- [ ] **Step 1: Create the helper**

Create `frontend/src/utils/time.js`:

```js
export function formatRelativeTime(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime()
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return 'most'
  if (diffMin < 60) return `${diffMin} perce`

  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} órája`

  const diffDay = Math.floor(diffHour / 24)
  return `${diffDay} napja`
}
```

Thresholds: under 1 minute → `"most"`, under 60 minutes → `"X perce"`, under
24 hours → `"X órája"`, otherwise → `"X napja"`.

- [ ] **Step 2: Verify**

No standalone test runner in this project. This is exercised visually in
Task 4 via the recent-saves timeline's relative-time labels.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/utils/time.js
git commit -m "Add formatRelativeTime helper for dashboard timeline"
```

---

### Task 4: Rewrite Dashboard.jsx with the Living Sigil design

**Files:**
- Modify (full rewrite): `frontend/src/pages/Dashboard.jsx`

- [ ] **Step 1: Replace the entire file contents**

Replace the full contents of `frontend/src/pages/Dashboard.jsx` with:

```jsx
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
```

- [ ] **Step 2: Verify the dev server compiles it**

```powershell
(Invoke-WebRequest -Uri "http://localhost:5173/src/pages/Dashboard.jsx" -UseBasicParsing).StatusCode
```

Expected: `200` (Vite serves the transformed module without a 500 error). If
Vite returns an error overlay/500, check `frontend.log` for the syntax error
and fix it before continuing.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx
git commit -m "Redesign Dashboard with Living Sigil hero, portal cards, and timeline"
```

---

### Task 5: Visual verification in the browser

**Files:** none (verification only)

- [ ] **Step 1: Confirm both servers respond**

```powershell
(Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode
(Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode
```

Expected: both `200`. If either fails, start them per `start-servers.ps1`.

- [ ] **Step 2: Screenshot the Dashboard with Playwright**

Run this Python script (adjust the python path to the working interpreter,
e.g. `C:\Users\Eylon\AppData\Local\Programs\Python\Python312\python.exe`):

```python
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto("http://localhost:5173/")
    page.wait_for_timeout(1500)  # let mount animations (fade-in, count-up) settle
    page.screenshot(path="dashboard-magus.png", full_page=True)

    # Hover the first portal card to capture the glow/lift hover state
    page.hover("text=Helyszín generálás")
    page.wait_for_timeout(400)
    page.screenshot(path="dashboard-portal-hover.png")

    browser.close()
```

- [ ] **Step 3: Review the screenshots**

Open `dashboard-magus.png` and `dashboard-portal-hover.png` and confirm:

- Centered rotating ring with the `⚔` icon visible inside it, title
  "MAGUS ARCHÍVUM" below with a visible gold glow
- Three stat pills below the subtitle, each showing a number (0, or higher if
  there are saved items) and a label (Mentett / Helyszín / NPC)
- Two portal cards side by side: left "Helyszín generálás" (gold icon
  outline), right "NPC generálás" (red/accent icon outline)
- In `dashboard-portal-hover.png`, the hovered "Helyszín generálás" card is
  lifted with a visible gold glow shadow and gold border
- A rune divider below the portal cards
- Either a vertical timeline of "Legutóbbi mentések" (if `localStorage` has
  saved items) or the centered "Az archívum üres." message (if empty)
- No layout overflow/clipping at 1280px width

- [ ] **Step 4: Clean up screenshot files**

These are temporary verification artifacts, not project assets:

```bash
rm -f dashboard-magus.png dashboard-portal-hover.png
```

No commit for this task — it's verification only.
