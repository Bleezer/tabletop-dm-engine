# ArchetypeManager Redesign — Tarot / Heraldic Cards

**Date:** 2026-06-04  
**Status:** Approved

## Summary

Replace the current two-panel (list + form) ArchetypeManager UI with a tarot/heraldic card design: a horizontal scrollable card strip at top, and an expanded "scroll panel" below the selected card.

## Layout

```
┌─ Page Header ──────────────────────────────────────────────┐
│  ARCHETÍPUS KÓDEX   (breadcrumb, title, subtitle, dots)    │
└────────────────────────────────────────────────────────────┘
┌─ Card Strip (horizontally scrollable) ─────────────────────┐
│  [⚔ Harcos Elit]  [🗡 Árnyék]  [☩ Pap]  [+ Új]           │
│  selected card raised + gold glow                          │
└────────────────────────────────────────────────────────────┘
     │ (connector line + diamond)
┌─ Scroll Panel ─────────────────────────────────────────────┐
│  gold top-bar glow                                         │
│  [icon]  NAME  /  description                              │
│  ├─ icon picker (12 emoji) + name field + desc textarea    │
│  ├─ ᚱᚢᚾᛖ divider                                          │
│  ├─ skill rows (roman numeral, name, fok badge, ▲▼, ✕)     │
│  └─ action bar: [✦ Pecsételés]  ● nem mentett  [Törlés]   │
└────────────────────────────────────────────────────────────┘
```

## Card design

- Fixed width: 108px, variable height
- Per-card accent color via CSS custom property `--card-accent`
- Hover: spring translateY(-8px) + scale(1.02) + shadow
- Selected: translateY(-10px) + gold border + glow ring
- Icon animates: float (4s), zoom on hover/selected
- Corner ornaments (◈) fade in on hover
- Pip dots show skill count (filled gold when selected)
- Each card has a colored top border strip

## Scroll Panel

- Gold top-bar with box-shadow glow
- Ambient radial gradient inside
- Header: large floating icon + Cinzel name + italic description
- Fields section: icon picker grid (12 options) + name input + textarea
- Skill list: roman numerals, Crimson Pro italic names, Alap/Mester badges
- Add-skill row: select + fok select + "+ Felvesz" button
- Action bar: blood-red "Pecsételés" with rotating ✦, pulsing dirty dot

## Animations

- Card hover: `cubic-bezier(.34,1.56,.64,1)` spring
- Icon: `float-icon` 4s ease-in-out loop
- Seal button ✦: 8s rotate loop
- Dirty dot: pulse-glow 2s loop
- Header ornament dots: staggered pulse-dot 3s

## Color palette (inherits from CSS vars)

```
--gold / --gold-lt / --gold-glow
--blood / --blood-lt
--ink / --parchment / --border / --border-md / --border-hi
--text / --text-dim / --text-faint
```

## Icon set

⚔ 🗡️ 🛡️ ☩ ✦ ☿ ♆ 🔥 👁️ ⚗️ 🌙 ♜

## Unchanged

- All API calls (listArchetipusok, getArchetipus, createArchetipus, updateArchetipus, deleteArchetipus, listKepzettsegek)
- State logic (selectedId, editor, dirty, saving, error)
- Route (/archetipusok), Sidebar nav item
