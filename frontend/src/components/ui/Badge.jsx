const COLORS = {
  default:  { bg: 'var(--th-surface2)', text: 'var(--th-muted)', border: 'var(--th-border)' },
  accent:   { bg: 'rgba(139,26,26,0.2)', text: 'var(--th-accent-lt)', border: 'var(--th-accent)' },
  gold:     { bg: 'rgba(201,149,14,0.15)', text: 'var(--th-gold-lt)', border: 'var(--th-gold)' },
  major:    { bg: 'rgba(139,26,26,0.25)', text: '#f87171', border: '#8b1a1a' },
  moderate: { bg: 'rgba(180,120,20,0.2)', text: '#fbbf24', border: '#b47820' },
  minor:    { bg: 'rgba(60,60,60,0.3)', text: 'var(--th-muted)', border: 'var(--th-border)' },
  friendly: { bg: 'rgba(20,90,20,0.3)', text: '#86efac', border: '#166534' },
  neutral:  { bg: 'rgba(50,80,80,0.3)', text: '#93c5fd', border: '#1e3a5f' },
  hostile:  { bg: 'rgba(139,26,26,0.3)', text: '#f87171', border: '#8b1a1a' },
}

const IMPORTANCE_LABEL = {
  major:    'főszereplő',
  moderate: 'mellékszereplő',
  minor:    'statiszta',
}

const ATTITUDE_COLOR = {
  barátságos: 'friendly',
  semleges:   'neutral',
  gyanakvó:   'default',
  ellenséges: 'hostile',
}

export default function Badge({ children, color = 'default', style: extra = {} }) {
  const c = COLORS[color] ?? COLORS.default
  return (
    <span
      style={{
        display: 'inline-block',
        background: c.bg,
        color: c.text,
        border: `1px solid ${c.border}`,
        borderRadius: '2px',
        padding: '0px 6px',
        fontSize: '0.7rem',
        fontFamily: 'var(--font-display)',
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        ...extra,
      }}
    >
      {children}
    </span>
  )
}

export function ImportanceBadge({ importance }) {
  return (
    <Badge color={importance}>
      {IMPORTANCE_LABEL[importance] ?? importance}
    </Badge>
  )
}

export function AttitudeBadge({ attitude }) {
  const color = ATTITUDE_COLOR[attitude] ?? 'default'
  return <Badge color={color}>{attitude}</Badge>
}
