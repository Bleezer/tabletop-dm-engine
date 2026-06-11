-- MAGUS RPG — SQLite schema
-- Database file: world/magus/magus.db
-- Each RPG system gets its own .db file (starwars, dnd, etc.)

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Dice formula registry
-- Shared lookup for every dice expression in the system:
--   property rolls, FP/ÉP per level, weapon damage, spell effects.
-- advantage = 1 means "roll twice, take the higher result" (2x notation).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dice_formulas (
    id          INTEGER PRIMARY KEY,
    formula     TEXT    NOT NULL UNIQUE,   -- canonical string, e.g. "3k6(2x)"
    dice_count  INTEGER NOT NULL DEFAULT 1,
    dice_sides  INTEGER NOT NULL,
    modifier    INTEGER NOT NULL DEFAULT 0,
    advantage   INTEGER NOT NULL DEFAULT 0 CHECK (advantage IN (0, 1)),
    avg         REAL    NOT NULL,
    min_val     INTEGER NOT NULL,
    max_val     INTEGER NOT NULL
);

-- ---------------------------------------------------------------------------
-- Classes (kasztok)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kasztok (
    id                      INTEGER PRIMARY KEY,
    nev                     TEXT    NOT NULL UNIQUE,

    -- Base combat values
    alap_ke                 INTEGER NOT NULL DEFAULT 0,
    alap_te                 INTEGER NOT NULL DEFAULT 0,
    alap_ve                 INTEGER NOT NULL DEFAULT 0,
    alap_ce                 INTEGER NOT NULL DEFAULT 0,

    -- Pain tolerance (fájdalomtűrési pont)
    -- alap_fp is a flat base; fp per level is a dice roll
    alap_fp                 INTEGER NOT NULL DEFAULT 0,
    fp_per_szint_formula_id INTEGER REFERENCES dice_formulas(id),

    -- Hit points (életerő pont)
    alap_ep                 INTEGER NOT NULL DEFAULT 0,

    -- Magic
    mana_per_szint          INTEGER NOT NULL DEFAULT 0,

    -- Skill points (képzettségpont)
    alap_kp                 INTEGER NOT NULL DEFAULT 0,
    kp_per_szint            INTEGER NOT NULL DEFAULT 0,

    -- Combat manoeuvre points (harcmodor)
    hm_per_szint            INTEGER NOT NULL DEFAULT 0,
    kotelezo_hm_te          INTEGER NOT NULL DEFAULT 0,  -- mandatory allocation to TÉ per level
    kotelezo_hm_ve          INTEGER NOT NULL DEFAULT 0,  -- mandatory allocation to VÉ per level

    -- Per-level % pool freely distributed among szazalekos skills
    szazalek_per_szint      INTEGER NOT NULL DEFAULT 0,

    -- HM distribution strategy (references codes.code_no for code_type='hm_elosztasi_mod')
    -- 1=TÉ/VÉ balance (gap 45)  2=all CÉ  3=all VÉ  4=all TÉ
    hm_elosztasi_mod        INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Property rolling formulas per class
-- Only rows for class-specific overrides; race defaults apply otherwise.
-- tulajdonsag values: ero, ugyesseg, gyorsasag, allokepesseg, egeszseg,
--                     szepseg, asztral, akarateroe, intelligencia, erzekeles
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kaszt_tulajdonsag_dobas (
    kaszt_id    INTEGER NOT NULL REFERENCES kasztok(id) ON DELETE CASCADE,
    tulajdonsag TEXT    NOT NULL,
    formula_id  INTEGER NOT NULL REFERENCES dice_formulas(id),
    PRIMARY KEY (kaszt_id, tulajdonsag)
);

-- ---------------------------------------------------------------------------
-- Special training: class can raise a stat 1 or 2 above racial maximum
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kaszt_spec_kepzetes (
    kaszt_id    INTEGER NOT NULL REFERENCES kasztok(id) ON DELETE CASCADE,
    tulajdonsag TEXT    NOT NULL,
    max_bonus   INTEGER NOT NULL CHECK (max_bonus IN (1, 2)),
    PRIMARY KEY (kaszt_id, tulajdonsag)
);

-- ---------------------------------------------------------------------------
-- Generic code table — configurable parameters keyed by (code_type, code_no)
-- code_type: category name (e.g. 'njk_tipus_min_pont')
-- code_no:   specific key  (e.g. 'atlagos', 'kiemelt', 'elit')
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS codes (
    code_type TEXT    NOT NULL,
    code_no   TEXT    NOT NULL,
    ertek     INTEGER NOT NULL,
    leiras    TEXT,
    PRIMARY KEY (code_type, code_no)
);

-- ---------------------------------------------------------------------------
-- Skills (képzettségek)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kepzettsegek (
    id           INTEGER PRIMARY KEY,
    nev          TEXT    NOT NULL UNIQUE,
    kategoria    TEXT    NOT NULL CHECK (kategoria IN ('harci', 'tudomanyos', 'vilagi', 'alvilagi')),
    tipus        TEXT    NOT NULL CHECK (tipus IN ('alap_mester', 'szazalekos')),
    ar_alapfok   INTEGER,    -- KP cost for alap fok; NULL if szazalekos or variable
    ar_mesterfok INTEGER     -- KP cost for mester fok; NULL if szazalekos
);

-- ---------------------------------------------------------------------------
-- Class starting skills and level-up skills
-- fok: 'alap', 'mester', 'kyr', 'slan' (Pszi levels),
--       '1'..'5' + 'mester' (Nyelvtudás proficiency levels)
-- szazalek: starting % for szazalekos skills (NULL for alap_mester skills)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kaszt_kepzettsegek (
    id              INTEGER PRIMARY KEY,
    kaszt_id        INTEGER NOT NULL REFERENCES kasztok(id),
    kepzettseg_id   INTEGER NOT NULL REFERENCES kepzettsegek(id),
    szint_tol       INTEGER NOT NULL DEFAULT 0,
    fok             TEXT    NOT NULL,
    szazalek        INTEGER
);

-- ---------------------------------------------------------------------------
-- XP thresholds per class and level
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kaszt_xp_kuszob (
    kaszt_id    INTEGER NOT NULL REFERENCES kasztok(id) ON DELETE CASCADE,
    szint       INTEGER NOT NULL,
    xp_min      INTEGER NOT NULL,
    PRIMARY KEY (kaszt_id, szint)
);

-- ---------------------------------------------------------------------------
-- Archetypes (archetípusok) — class-independent skill priority lists
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS archetipusok (
    id          INTEGER PRIMARY KEY,
    nev         TEXT    NOT NULL UNIQUE,
    leiras      TEXT,
    ikon        TEXT    NOT NULL DEFAULT '⚔',
    letrehozva  TEXT    NOT NULL DEFAULT (datetime('now')),
    frissitve   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Skills belonging to an archetype, ordered by priority
CREATE TABLE IF NOT EXISTS archetipus_kepzettsegek (
    id              INTEGER PRIMARY KEY,
    archetipus_id   INTEGER NOT NULL REFERENCES archetipusok(id) ON DELETE CASCADE,
    kepzettseg_id   INTEGER NOT NULL REFERENCES kepzettsegek(id),
    prioritas       INTEGER NOT NULL DEFAULT 0,
    cel_fok         TEXT    NOT NULL DEFAULT 'alap'
);

-- ---------------------------------------------------------------------------
-- Generated characters (PCs and NPCs)
-- Core generation data is stored as JSON; narrative fields are nullable and
-- can be filled in later (manually or via the Claude API pipeline).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS karakterek (
    id          INTEGER PRIMARY KEY,

    -- Generation seed
    kaszt       TEXT    NOT NULL,
    szint       INTEGER NOT NULL,
    njk_tipus   TEXT    NOT NULL DEFAULT 'atlagos',
    faj         TEXT,                -- from npc_generator concept
    szerep      TEXT,                -- role in location context

    -- Rolled stats (JSON objects)
    tulajdonsagok   TEXT NOT NULL,   -- {"ero": 14, "ugyesseg": 12, ...}
    harci_ertekek   TEXT NOT NULL,   -- {"ke": 10, "te": 25, "ve": 65, "ce": 5, "kp": 30, "ep": 18, "fp": 42, ...}

    -- Identity
    nev         TEXT,
    nem         TEXT,
    kor_leiras  TEXT,

    -- Narrative (from Claude API or manual)
    megjelenes  TEXT,
    szemelyiseg TEXT,
    elotortenete TEXT,
    szolasmod   TEXT,
    motivacio   TEXT,
    titok       TEXT,
    idegenekhez_viszonyulas TEXT,

    -- Equipment and goals (JSON arrays, filled in later)
    felszereles TEXT,   -- [{"nev": "kard", "megjegyzes": "..."}, ...]
    celok       TEXT,   -- ["Megtorolni a klán halálát", ...]

    megjegyzesek TEXT,

    -- Metadata
    letrehozva  TEXT    NOT NULL DEFAULT (datetime('now')),
    frissitve   TEXT    NOT NULL DEFAULT (datetime('now'))
);
