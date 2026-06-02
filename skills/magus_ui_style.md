# Dark Fantasy RPG Dungeon Master Tools – Style Skill

## Role

You are a senior product designer and frontend UI stylist. Your task is to restyle an existing Dungeon Master tools web application into a serious, elegant dark fantasy RPG interface inspired by Hungarian M.A.G.U.S. / Ynev atmosphere.

The website already exists. Do not redesign the product logic. Do not remove functionality. Your job is to create and apply a coherent visual style system.

The app contains tools such as:

* character generator
* NPC generator
* location generator
* faction / house generator
* adventure hooks
* campaign notes
* timeline / event tools
* secret GM information panels

The style must support practical use during tabletop RPG preparation and play.

---

## Core Design Goal

Create the feeling of a dark fantasy game master's archive: part noble house ledger, part forbidden chronicle, part war council dossier, part occult field notebook.

The interface must be atmospheric, but still usable.

Priority order:

1. readability
2. usability
3. consistency
4. dark fantasy atmosphere
5. decorative detail

Never sacrifice usability for ornament.

---

## Visual Identity

The app should feel:

* dark
* elegant
* ancient
* political
* dangerous
* serious
* ritualistic
* archival
* practical for a game master

It should not feel:

* cartoonish
* generic D&D tavern fantasy
* colorful high fantasy
* modern SaaS dashboard
* mobile game UI
* neon gamer interface
* World of Warcraft-like
* AI image generator clutter
* overdecorated gothic mess

The style should suggest stone, parchment, blood, wax seals, old ink, tarnished metal, heraldry, old maps, noble documents and forbidden magical diagrams.

---

## Color Palette

Use a dark base with restrained accent colors.

### Base colors

```css
--bg-main: #0b0b0d;
--bg-panel: #141114;
--bg-panel-raised: #1b1718;
--bg-muted: #221d1d;
--border-subtle: #3a2f2f;
--border-strong: #6b4b2e;
```

### Text colors

```css
--text-main: #e7dcc8;
--text-muted: #b8aa94;
--text-faint: #7d7164;
--text-danger: #c46a5a;
```

### Accent colors

```css
--accent-gold: #b08a4a;
--accent-blood: #7a1e1e;
--accent-blood-bright: #a83232;
--accent-silver: #9ca3af;
--accent-parchment: #d6c29a;
--accent-green-dark: #263a2d;
```

### Usage

Gold is for hierarchy, selected states, borders, important labels.

Blood red is for danger, secrets, warnings, destructive actions, occult elements.

Silver is for secondary metadata, inactive noble / military elements.

Parchment is for readable content blocks, notes and generated text.

Do not use bright primary colors except very sparingly.

---

## Typography

Use a serious readable serif/sans pairing.

Suggested:

* Headings: `Cinzel`, `Cormorant Garamond`, `Spectral SC`, or similar
* Body: `Inter`, `Source Sans 3`, `Lora`, or `Merriweather Sans`
* Generated lore text: serif preferred
* Form controls and buttons: readable sans preferred

Rules:

* Headings should feel noble and engraved, not cheesy gothic.
* Body text must be easy to read.
* Avoid overly decorative blackletter fonts.
* Avoid tiny grey text.
* Line height should be comfortable.

Example:

```css
h1, h2, h3 {
  font-family: "Cinzel", serif;
  letter-spacing: 0.04em;
  color: var(--accent-parchment);
}

body {
  font-family: "Inter", sans-serif;
  color: var(--text-main);
}
```

---

## Layout Principles

The app should feel like a tool, not a landing page.

Use:

* clear side navigation
* strong section headers
* cards for tools
* panels for generated outputs
* tabs for switching between categories
* collapsible sections for advanced / secret information
* visible hierarchy

Avoid:

* huge empty hero sections inside the app
* too much decorative whitespace
* unreadable background images behind text
* excessive animation
* buried controls

The UI should work well during a live RPG session.

---

## Component Style

### App Shell

The main app background should be very dark, with subtle texture if possible.

Navigation should feel like a leather-bound index or war council sidebar.

Sidebar style:

* dark stone / leather background
* thin gold or bronze borders
* muted icons
* active item highlighted with blood-red or antique gold accent
* no bright blue SaaS styling

---

### Cards

Cards should look like dark parchment / archive panels.

```css
.card {
  background: linear-gradient(180deg, #1b1718, #120f10);
  border: 1px solid #3a2f2f;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.45);
}
```

Important cards may have a subtle gold top border.

Secret / dangerous cards may have a subtle blood-red side border.

---

### Buttons

Primary button:

* antique gold or deep blood red
* not bright
* slight bevel / border
* strong hover state

Secondary button:

* dark background
* bronze border
* parchment text

Danger button:

* blood red
* restrained, not neon

Button labels should be practical:

* Generate NPC
* Create Location
* Save to Campaign
* Reveal Secret
* Regenerate
* Export Notes

---

### Forms

Forms are central. They must be clean.

Inputs should be:

* dark
* bordered
* high contrast
* clearly focused
* not overdecorated

Textarea for prompts and generated content should feel like a writing desk / archive note, but still be readable.

Focus state:

```css
outline: none;
border-color: var(--accent-gold);
box-shadow: 0 0 0 2px rgba(176, 138, 74, 0.25);
```

---

### Generated Output Panels

Generated characters, places and factions should appear as structured dossiers.

Example layout:

**NPC Name**
Role / faction / threat level

Sections:

* Appearance
* Personality
* Public Goal
* Hidden Motive
* Useful Secret
* How to Play Them
* Hooks

Generated text should not appear as one giant blob. Use structured blocks.

For secrets, use collapsible dark-red panels:

Label: `GM Secret`, `Hidden Motive`, `Forbidden Knowledge`.

---

### Tags and Badges

Use badges for:

* faction
* danger level
* region
* race / culture
* magic
* political role
* secret

Badge styles:

* muted background
* thin border
* small caps
* no bright colors

Examples:

```text
TORONI NOBILITY
DEMONIC TRACE
POLITICAL THREAT
GM ONLY
```

---

### Tables

Tables should look like ledgers.

Use:

* dark rows
* subtle alternating background
* gold headers
* thin borders
* compact but readable spacing

Useful for:

* NPC lists
* faction lists
* timeline
* saved locations
* campaign entities

---

### Accordions / Collapsible Sections

Use for:

* advanced generator settings
* secret information
* optional lore
* GM-only spoilers

Closed state should be compact.

Open state should feel like unfolding a sealed document.

---

## Iconography

Use restrained line icons.

Good motifs:

* quill
* scroll
* wax seal
* dagger
* tower
* raven
* shield
* map
* eye
* key
* flame
* skull, only sparingly

Avoid cartoon icons.

---

## Motion

Animations must be subtle.

Allowed:

* slow hover lift
* border glow
* accordion expansion
* fading generated result
* subtle ember / smoke background only if performance-safe

Not allowed:

* bouncing
* spinning
* flashy transitions
* particle overload
* constant distracting movement

---

## Content Tone

UI labels should be practical, but flavor can appear in headings and empty states.

Good examples:

```text
No saved NPCs yet.
The archive is empty.

Generate Location
Shape a place worth fearing.

GM Secret
This information is not meant for players.

Campaign Ledger
Saved people, places and unresolved dangers.
```

Avoid jokes, memes, modern slang or overly epic clichés.

---

## DM Tool Specific Rules

### Character Generator

The generated character card should include:

* name
* role
* origin / culture
* appearance
* voice / manner
* motivation
* secret
* immediate use at the table

The UI should make it easy to copy, save, regenerate or expand the character.

### Location Generator

Locations should be shown like field reports.

Sections:

* First Impression
* Important Areas
* People Present
* Hidden Danger
* Sensory Details
* Encounter Hooks

Use map-like visual motifs.

### Faction / Noble House Generator

Use heraldic styling.

Sections:

* House Name
* Colors
* Symbol
* Public Reputation
* Real Power
* Allies
* Enemies
* Current Scheme

Display colors and symbol as badges or miniature heraldic blocks.

### Adventure Hook Generator

Hooks should be displayed as cards with:

* premise
* complication
* hidden truth
* possible player choices
* escalation

### Campaign Notes

Campaign notes should look like a chronicle or ledger.

Support:

* tags
* dates
* faction links
* secret notes
* unresolved threads

---

## Accessibility

Do not use low contrast text.

Text must be readable on all backgrounds.

Do not place long text directly over images.

Interactive elements must have visible focus states.

The app must be usable without relying only on color.

---

## Implementation Rules

When modifying existing code:

* preserve existing functionality
* do not rename business logic unnecessarily
* do not remove forms, buttons or data
* improve styling through reusable classes/components
* centralize colors into CSS variables or theme tokens
* create a consistent component system
* avoid one-off inline styles
* make the style reusable across future pages

---

## Final Quality Bar

The result should look like a serious dark fantasy Game Master workstation.

It should feel custom-built for a M.A.G.U.S. / Ynev-style campaign, but without using copyrighted logos or official assets.

It should be atmospheric enough to inspire the GM, but clean enough to use during an actual game session.


First inspect the existing UI structure. Then create a reusable theme system. Do not start by rewriting the whole app. Identify repeated components: layout, sidebar, cards, forms, buttons, generated output panels, tables, modals. Apply the dark fantasy style through shared tokens and reusable classes. After that, update the main screens one by one.


Do not make it look like a landing page. This is a working tool for a Dungeon Master. Keep controls obvious, forms readable, and generated output structured.
