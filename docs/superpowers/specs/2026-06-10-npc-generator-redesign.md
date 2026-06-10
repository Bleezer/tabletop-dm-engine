# NPC Generator Redesign — Field Dossier

**Date:** 2026-06-10
**Status:** Approved

## Summary

Restyle `NpcGenerator.jsx` ("NPC Generálás") in the same dark-fantasy ledger
language established by the Archetípus Kódex and Dashboard redesigns. The
shared `<Header>` is replaced by a bespoke "Command Ledger" header (pulsing
gold underline, floating page icon). The input panel becomes a gold-topped
archive panel with ledger-style example-role tags and a seal-icon generate
button. The generated NPC dossier gets a new horizontal "vitals bar" for core
combat values, and the narrative/attribute panels move to a uniform dark
ledger look (replacing the parchment paper-card), fixing a pre-existing
dark-on-dark contrast bug in `StatRow` along the way.

## Layout

```
┌─ Header ────────────────────────────────────────────────────────┐
│  Magus · Mesélői Eszközök                                  †      │
│  NPC GENERÁLÁS                                                    │
│  "Önálló karakter létrehozása — faj, kaszt és szint..."           │
│  ▬▬▬▬▬ (pulsing gold underline, ~25% width)                       │
└────────────────────────────────────────────────────────────────┘
┌─ Input Panel (archive-panel-gold) ───────────────────────────────┐
│  SZEREP / RÖVID LEÍRÁS                                            │
│  [ ___________________________________________ ]                 │
│  (Fogadós) (Őr) (Tolvaj) (Kereskedő)        ← ledger pills        │
│                                                                    │
│  HELYSZÍN KONTEXTUS (opcionális)                                  │
│  [ ___________________________________________ ]                 │
│  [ ___________________________________________ ]                 │
│                                                                    │
│                                          [ ✦ NPC generálása ]     │
└────────────────────────────────────────────────────────────────┘
                          ⬥  (RuneDivider)
┌─ Dossier ─────────────────────────────────────────────────────────┐
│  SARN KAEL (gold glow)              [mellékszereplő] ✓ #12        │
│  Ranzeári íjász, 4. szint                                          │
│                                                                     │
│  ┌─ Vitals bar ───────────────────────────────────────────────┐  │
│  │  KÉ   TÉ   VÉ   CÉ   ÉP   FP                                │  │
│  │  62   58   45   38   24   31                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─ Left (archive-panel) ──────┐  ┌─ Right (archive-panel ×2) ──┐ │
│  │ [gender][age][attitude]      │  │ Tulajdonságok                │ │
│  │ Megjelenés                   │  │  Erő     14                  │ │
│  │ Személyiség                  │  │  Áll     11                  │ │
│  │ Háttér                       │  │  ...                         │ │
│  │ Motiváció                    │  │                              │ │
│  │ „speech style quote"         │  │ Meta                         │ │
│  │ ▼ Mesélői titok               │  │  Összpont   84               │ │
│  └──────────────────────────────┘  │  Szerep     fogadós          │ │
│                                     └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Header (replaces shared `<Header>`)

Inline JSX, following the pattern established in `ArchetypeManager.jsx`
(no shared component — page-specific markup):

- Eyebrow line "Magus · Mesélői Eszközök" — unchanged styling (Cinzel,
  0.62rem, `--th-faint`, uppercase, letter-spacing 0.22em)
- Title "NPC Generálás" — Cinzel, gold, uppercase, unchanged size/weight from
  current `<Header>` h2
- A small **†** icon floats on the right side of the title row
  (`arch-float`, 4s ease-in-out infinite), `--th-gold`, ~1.1rem — echoes the
  red "NPC generálás" portal icon from the Dashboard
- Subtitle — unchanged copy and styling (italic, Crimson Pro, `--th-faint`)
- New: a thin pulsing gold underline accent — `position: absolute`,
  `bottom: -1px`, `left: 0`, `width: 25%`, `height: 2px`,
  `background: var(--th-gold)`, animation `arch-pulse-glow` 2.5s
  ease-in-out infinite (reuses the existing keyframe — its opacity+box-shadow
  pulse works for a thin bar)
- Header keeps `border-bottom: 1px solid var(--th-border)` and needs
  `position: relative` for the underline to anchor against

## Input Panel

- Wraps in the existing `.archive-panel.archive-panel-gold` classes (gradient
  surface background + 2px gold top border) instead of the current ad-hoc
  inline gradient/border styles
- "Szerep / rövid leírás" label — unchanged styling and copy
- Role-hint `<input className="th-input">` — unchanged behavior (Enter to
  submit, placeholder, disabled while loading)
- Example-role tags — restyled as small ledger pills directly below the
  input: Cinzel, ~0.62rem, uppercase, letter-spacing 0.08em, `1px solid
  var(--th-border-strong)`, `color: var(--th-faint)`, `border-radius: 2px`,
  `padding: 2px 10px`. On hover: `border-color: var(--th-gold)`,
  `color: var(--th-gold)`, `background: rgba(176,138,74,0.08)`. Same 4
  `EXAMPLE_ROLES`, same click-to-fill behavior.
- "Helyszín kontextus (opcionális)" label + textarea — unchanged
- Generate button — `<Button variant="primary">`, unchanged disabled logic.
  When idle, prefix the label with a small inline `✦` span animated with
  `arch-seal-rotate` 8s linear infinite (matches the Archetípus Kódex save
  button). While `loading`, the button is disabled as today and the page-level
  `<Spinner label="NPC generálása..." size={36} />` still renders below (the
  seal icon is cosmetic on the idle button only — no extra loading state
  inside the button itself).

## Divider

Insert `<RuneDivider symbol="⬥" />` between the input panel and the
loading/error/result area (this also makes use of the currently-unused
`RuneDivider` import).

## Dossier Banner

- NPC name (`char.name`) — Cinzel, uppercase, increase emphasis with
  `text-shadow: 0 0 20px var(--th-gold-glow)` in addition to the existing
  gold color/size
- Race/class/level subtitle — unchanged
- `<ImportanceBadge>` and the optional `✓ #{npc.id}` saved indicator —
  unchanged, right-aligned as today

## Vitals Bar

Replaces the current 3-column "Harci értékek" box. New full-width horizontal
strip placed between the dossier banner and the 2-column body:

- Container: `display: flex`, `border: 1px solid var(--th-border)`,
  `border-radius: 4px`, `overflow: hidden`,
  `background: linear-gradient(180deg, var(--th-surface2), var(--th-surface))`
- One cell per stat, `flex: 1`, `border-right: 1px solid var(--th-border)`
  (last cell no border), `text-align: center`, `padding: 0.5rem 0.25rem`
- Each cell: bold gold value (Cinzel, ~1.05rem, `--th-gold`) over a faint
  uppercase label (~0.55rem, `--th-faint`, letter-spacing 0.1em)
- **Stats and order** (corrected from the original 3×2 grid): KÉ, TÉ, VÉ, CÉ,
  ÉP, FP — sourced from `sb.combat.ke`, `.te`, `.ve`, `.ce`, `.ep`, `.fp`
  respectively. The old `HM` cell (`sb.combat?.hm`) is dropped — `hm` here is
  `szabad_hm_ossz` (free HM pool), not a player-facing vital, and `FP`
  (Fárasztó Pont / fatigue) is the correct sixth combat value.
- Filter `[, v] => v != null` as before; if all are null, the vitals bar is
  omitted entirely.

## Dossier Body

2-column grid (`1fr 1fr`, `gap: 1.25rem`), unchanged column proportions.

**Left column** — `.archive-panel` (dark gradient, `--th-border`), padding
`1.25rem`, replacing `.paper-card`:

- Badges row (gender, age_description via `Badge`, `<AttitudeBadge>`) —
  unchanged
- `DossierField` — body text color changes from `--th-ink` to `--th-text`
  (the parchment-tuned near-black no longer applies on a dark panel); label
  stays `--th-faint` (already legible on dark)
- Speech-style quote — text color changes from `--th-ink-muted` to
  `--th-muted`; left border changes from `--th-paper-dk` to
  `--th-border-strong`
- Collapsible "Mesélői titok" — unchanged; `.secret-block` and the ▲/▼
  toggle button already render correctly on dark backgrounds

**Right column** — two `.archive-panel` blocks stacked (`gap: 0.75rem`,
unchanged from current):

- "Tulajdonságok" panel — unchanged header label and `Object.entries(sb.stats)`
  iteration via `STAT_HU`, vertical `StatRow` list (per user choice, not a
  grid)
- "Meta" panel — unchanged, `StatRow` for "Összpont" (`sb.total_points`) and
  "Szerep" (`conc.role`)

**`StatRow` fix** (shared by both right-column panels — currently used
exclusively on dark backgrounds but styled with parchment-ink colors,
making values nearly invisible):

- Label color: `--th-ink-muted` → `--th-muted`
- Value color: `--th-ink` → `--th-gold-lt`, keep `font-weight: 600`
- Border-bottom: `1px solid rgba(0,0,0,0.1)` → `1px solid var(--th-border)`

## Animations (all reused from existing `index.css` — no new keyframes)

- `arch-pulse-glow` — header underline pulse
- `arch-float` — header's floating † icon
- `arch-seal-rotate` — rotating ✦ on the idle generate button
- `.fade-in` / `fadeIn` — `NpcResult` mount animation, unchanged

## Unchanged

- Route (`/npc`), sidebar nav item
- `generateNpc(locationCtx, roleHint)` API call and `handleGenerate` logic
- `EXAMPLE_ROLES` content and click-to-fill behavior
- Loading (`<Spinner label="NPC generálása..." size={36}/>`) and error block
  styling/placement
- `STAT_HU` label mapping
- Secret reveal/hide toggle behavior
