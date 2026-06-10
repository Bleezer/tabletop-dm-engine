# Dashboard Redesign — Living Sigil

**Date:** 2026-06-10
**Status:** Approved

## Summary

Replace the current compact header + QuickAction grid with a "Living Sigil" hero:
a centered rotating emblem ring around the active theme's icon, a glowing title,
the existing lore subtitle, and three animated stat pills with count-up numbers.
Below, two large "portal" action cards (gold / red accents) replace the current
2-column QuickAction grid, followed by a vertical timeline of recent saves with
a pulsing "most recent" indicator.

## Layout

```
┌─ Hero ───────────────────────────────────────────────────────┐
│                     ╭───╮                                      │
│                     │ ⚔ │   (rotating ring, counter-rotating   │
│                     ╰───╯    icon — theme.icon)                │
│                                                                  │
│              MAGUS ARCHÍVUM      (Cinzel, gold glow text)       │
│      "A sötétség leszáll Erionra..."   (Crimson Pro, italic)    │
│                                                                  │
│   ( 7 Mentett )   ( 4 Helyszín )   ( 3 NPC )   (pulsing pills)  │
└──────────────────────────────────────────────────────────────┘
┌─ Portal cards (2-col grid) ─────────────────────────────────────┐
│  [ ⌖  Helyszín generálás ]   gold accent, glow on hover         │
│  [ †  NPC generálás      ]   red accent, glow on hover          │
└──────────────────────────────────────────────────────────────┘
                          ⬥ ⬥ ⬥   (RuneDivider, unchanged)
┌─ Legutóbbi mentések (vertical timeline) ────────────────────────┐
│  ●─ Régi Kikötő     Kereskedői negyed              2 perce       │
│  │─ Sarn Kael       Ranzeári íjász, 4. szint       14 perce      │
│  │─ Romos Templom   Szent hely                     1 órája       │
│  ╵─ Voldar          Pyarroni varázsló, 7. szint    3 órája       │
└──────────────────────────────────────────────────────────────┘
```

## Hero ("Living Sigil")

- Full width, centered, sits directly on page background (`--th-bg`) — no
  separate surface-colored header bar.
- **Ring**: 68px circle, 2px solid `--th-gold` border with top & bottom edges
  transparent (gives a "broken ring" / armillary look), `box-shadow: 0 0 18px
  var(--th-gold-glow)`. Animation: `arch-seal-rotate` 7s linear infinite.
- **Inner icon**: `theme.icon` (⚔ for magus, ✦ for starwars), centered inside
  the ring, ~1.5rem, `--th-gold`. Animation: `arch-seal-rotate` 7s linear
  infinite, `animation-direction: reverse` (counter-rotates against the ring —
  "gear" effect).
- **Title**: existing theme-dependent text ("MAGUS Archívum" / "Star Wars
  Archívum"), Cinzel, ~1.6rem, font-weight 700, letter-spacing 0.22em,
  `--th-gold`, `text-shadow: 0 0 24px var(--th-gold-glow)`.
- **Subtitle**: existing theme-dependent lore paragraph, Crimson Pro italic,
  `--th-faint`, unchanged copy.
- **Stat pills**: row of 3 pill-shaped badges (border `--th-border`,
  `border-radius: 999px`) — Mentett / Helyszín / NPC counts (same filters as
  today). Each pill: `arch-pulse-border` animation (new, see below), staggered
  delays (0s / 0.4s / 0.8s). The number inside each pill counts up from 0 on
  mount (see below).

## Count-up stat numbers (new behavior)

- New small hook `useCountUp(target, duration = 900)` in
  `frontend/src/hooks/useCountUp.js`: returns the current animated value,
  driven by `requestAnimationFrame`, easing the count from 0 to `target` over
  `duration` ms. Re-triggers if `target` changes.
- Used for the 3 numbers inside the stat pills.

## Portal Cards

- Replace the `QuickAction` 2-column grid with two larger "portal" cards
  (same 1fr 1fr grid).
- Shared structure: bordered card, `radial-gradient` glow at top-center
  (color depends on accent), centered icon in a circular outline, Cinzel
  uppercase title, italic Crimson Pro description.
- Two accent variants:
  - **gold** (⌖ Helyszín generálás → `/location`): gold border/icon/glow.
  - **red** († NPC generálás → `/npc`): `--th-accent-lt` /
    `--th-accent-glow` border/icon/glow.
- Icon floats continuously (`arch-float`, 4.5s); the red card's icon has a
  +0.3s delay so the two don't move in lockstep.
- Hover: `translateY(-5px)`, border switches to the accent color, box-shadow
  glow in the accent color, `cubic-bezier(.34,1.56,.64,1)` spring transition.
- Both cards fade/slide in on mount via the existing `.fade-in` class
  (`fadeIn` keyframe), red card delayed ~0.1s after gold.

## Recent Saves — Vertical Timeline

- Replace the flat `RecentCard` list with a vertical timeline (max 4 items,
  same `saved.slice(0, 4)` data).
- Left rail: 1px vertical line, `linear-gradient(to bottom, var(--th-gold),
  var(--th-border))`, with a small circular dot per item (gold border, page-bg
  fill) positioned on the rail.
- The **first item's dot** additionally pulses via `arch-pulse-dot` (it's the
  most recent save).
- Each row: type icon (⌖ location / † npc), title, subtitle (same fields as
  current `RecentCard`), and a right-aligned **relative time** computed from
  `item.savedAt` (e.g. "2 perce", "14 perce", "1 órája", "3 napja").
- Rows fade/slide in from the left via the existing `arch-dirty-in` keyframe,
  staggered ~0.08s per item.
- Hover: row background → `--th-surface2`.
- Click → `navigate('/saved')` (unchanged).

## Relative time helper

- New small util `formatRelativeTime(isoString)` (co-located in
  `Dashboard.jsx` or `frontend/src/utils/time.js`): returns elapsed time since
  `savedAt`, with thresholds: < 1 min → "most", < 60 min → "X perce", < 24h →
  "X órája", otherwise → "X napja".

## Empty State

- When `saved.length === 0`, the timeline area is replaced by the existing
  centered, faint "Az archívum üres." message (unchanged copy/styling),
  simply positioned under the new hero/portals instead of the old layout.

## Animations — mostly reused from existing `index.css`

- `arch-seal-rotate` — hero ring (7s) and, reversed, the inner theme icon
- `arch-pulse-border` — stat pills (staggered delays) — **new**, box-shadow-only
  pulse (no opacity change, unlike `arch-pulse-glow`):
  ```css
  @keyframes arch-pulse-border {
    0%, 100% { box-shadow: 0 0 4px var(--th-gold-glow); }
    50%       { box-shadow: 0 0 12px var(--th-gold-glow); }
  }
  ```
- `fadeIn` / `.fade-in` — portal cards (staggered)
- `arch-float` — portal card icons
- `arch-pulse-dot` — timeline's "most recent" dot
- `arch-dirty-in` — timeline row stagger-in

## Color Palette (inherits from CSS vars)

```
--th-gold / --th-gold-lt / --th-gold-glow   → ring, title, gold portal, pills
--th-accent-lt / --th-accent-glow           → red portal accent
--th-text / --th-muted / --th-faint         → body text, subtitles, timestamps
--th-border / --th-border-strong            → card borders, timeline rail
--font-display (Cinzel) / --font-lore (Crimson Pro)
```

## Unchanged

- Route (`/`), Sidebar nav item ("Főoldal")
- Data sources: `useSaved()` (`saved`, `item.savedAt`, `item.type`,
  `item.data`), `useTheme()` (`themeId`, `theme.icon`)
- Theme-dependent title/subtitle copy logic
- Stat counts: total / `type === 'location'` / `type === 'npc'` filters
- Quick action targets: `/location`, `/npc`
- Recent item click → `/saved`
- `RuneDivider` component between portals and recent saves
